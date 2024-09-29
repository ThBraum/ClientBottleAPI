from datetime import datetime
from io import BytesIO
import calendar
import os
import boto3
from sqlalchemy import select, extract
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.legends import Legend
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.widgets.markers import makeMarker
import logging
from fastapi import HTTPException, status

from server.configuration.database import DepDatabaseSession
from server.model.client_bottle_transaction import ClientBottleTransaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY in environment variables",
    )

try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="sa-east-1",
    )
except Exception as e:
    logger.error(f"Failed to connect to S3: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to S3"
    )

bucket_name = "client-bottle"


async def generate_pdf(session: DepDatabaseSession):
    current_year = datetime.now().year
    current_month = datetime.now().month

    months_pt_br = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]
    month_name = months_pt_br[datetime.now().month - 1]

    last_day = calendar.monthrange(current_year, current_month)[1]

    query_active = select(ClientBottleTransaction).where(
        ClientBottleTransaction.fl_active == True,
        extract("month", ClientBottleTransaction.transaction_date) == current_month,
    )
    query_inactive = select(ClientBottleTransaction).where(
        ClientBottleTransaction.fl_active == False,
        extract("month", ClientBottleTransaction.transaction_date) == current_month,
    )

    result_active = await session.execute(query_active)
    result_inactive = await session.execute(query_inactive)

    transactions_active = result_active.scalars().all()
    transactions_inactive = result_inactive.scalars().all()

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    days_in_month = range(1, last_day + 1)

    active_counts = [
        sum(
            item["quantity"]
            for t in transactions_active
            if t.transaction_date.day == day
            for item in t.transaction_data_json
        )
        for day in days_in_month
    ]
    inactive_counts = [
        sum(
            item["quantity"]
            for t in transactions_inactive
            if t.transaction_date.day == day
            for item in t.transaction_data_json
        )
        for day in days_in_month
    ]

    drawing_width = 570
    drawing = Drawing(drawing_width, 300)

    rectangle_width = drawing_width - 110
    drawing.add(Rect(-50, 0, rectangle_width, 300, fillColor=colors.lightblue))

    line_chart = LinePlot()
    line_chart.x = -25
    line_chart.y = 50
    line_chart.width = rectangle_width - 70
    line_chart.height = 200

    line_chart.data = [
        list(zip(days_in_month, active_counts)),
        list(zip(days_in_month, inactive_counts)),
    ]

    line_chart.lines[0].strokeColor = colors.red
    line_chart.lines[0].symbol = makeMarker("Square")
    line_chart.lines[0].strokeWidth = 1.5

    line_chart.lines[1].strokeColor = colors.blue
    line_chart.lines[1].symbol = makeMarker("Circle")
    line_chart.lines[1].strokeWidth = 1.5

    line_chart.xValueAxis.valueMin = 1
    line_chart.xValueAxis.valueMax = last_day
    line_chart.xValueAxis.valueStep = 2
    line_chart.xValueAxis.labelTextFormat = "%d"
    line_chart.yValueAxis.valueMin = 0
    line_chart.yValueAxis.valueMax = 350
    line_chart.yValueAxis.valueStep = 50

    for day, active, inactive in zip(days_in_month, active_counts, inactive_counts):
        x_position = line_chart.x + ((day - 1) * (line_chart.width / (last_day - 1)))

        if active > 0:
            y_position_active = line_chart.y + (active * (line_chart.height / 350))
            drawing.add(
                String(
                    x_position - 7,
                    y_position_active + 5,
                    str(active),
                    fillColor=colors.red,
                )
            )

        if inactive > 0:
            y_position_inactive = line_chart.y + (inactive * (line_chart.height / 350))
            drawing.add(
                String(
                    x_position - 7,
                    y_position_inactive + 5,
                    str(inactive),
                    fillColor=colors.blue,
                )
            )

    legend = Legend()
    legend.x = 440
    legend.y = 230
    legend.alignment = "right"
    legend.boxAnchor = "nw"
    legend.columnMaximum = 10
    legend.fontName = "Helvetica"
    legend.fontSize = 10
    legend.strokeWidth = 1
    legend.strokeColor = colors.black
    legend.deltax = 75
    legend.deltay = 10
    legend.autoXPadding = 5
    legend.yGap = 0
    legend.dxTextSpace = 5
    legend.dy = 5
    legend.colorNamePairs = [(colors.red, "Emprestadas"), (colors.blue, "Devolvidas")]

    drawing.add(line_chart)
    drawing.add(legend)

    elements.append(Spacer(1, 12))
    elements.append(drawing)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title = Paragraph(f"Transações para o mês de {month_name}", title_style)
    elements.insert(0, title)

    pdf.build(elements)
    buffer.seek(0)

    return buffer


async def upload_pdf_to_s3(buffer: BytesIO, bucket_name: str, file_name: str):
    try:
        s3_client.upload_fileobj(buffer, bucket_name, file_name)
        logger.info(f"File {file_name} uploaded successfully to {bucket_name}.")
        return f"https://{bucket_name}.s3.sa-east-1.amazonaws.com/{file_name}"
    except Exception as e:
        logger.error(f"Failed to upload file {file_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload file to S3"
        )
