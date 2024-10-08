FROM python:3.11-buster AS python_base

WORKDIR /app
ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PATH="/app/.venv/bin:${PATH}"

FROM python_base AS poetry_base

ARG POETRY_VERSION=1.7.1
RUN pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.in-project true

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --only main

FROM node:21.6.1-bullseye AS template_builder

WORKDIR /templates/email
RUN npm install mjml
COPY ./templates /templates

RUN mkdir /build && \
    for template in *.mjml; do \
        npx mjml $template \
            --config.minify true \
            --config.minifyOptions='{"minifyCSS": true, "removeEmptyAttributes": true}' \
            > /build/$(basename $template .mjml).html; \
    done

FROM python_base

COPY --from=poetry_base /app /app/
COPY --from=template_builder /build /app/templates/email
COPY ./exec /app/exec
COPY ./server /app/server
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

ARG VERSION
ARG MODE
ARG ALGORITHM

ENV VERSION=${VERSION}
ENV MODE=${MODE}
ENV ALGORITHM=${ALGORITHM}

HEALTHCHECK CMD [ "bash", "/app/exec/healthcheck.sh" ]
CMD [ "bash", "/app/exec/start.sh" ]
