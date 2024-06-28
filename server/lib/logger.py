import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

import pytz

from server.lib.terminalutils import text_colored


def setup_logging():
    log_level = logging.DEBUG

    logger = logging.getLogger("bottle_api")
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    logger.addHandler(handler)

    tz = pytz.timezone("America/Sao_Paulo")
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    formatter.converter = lambda *args: datetime.datetime.now(tz).timetuple()

    handler.setFormatter(formatter)
    return logger


logger = setup_logging()


def log_progress(value, base, verbose=0):
    """
    Generates progress bars for Linux terminal using the logging module.
    """
    if verbose > 0:
        progress = round(100 * (value + 1.0) / base)
        progress_bar = text_colored("blue", "=") * int(progress / 4)
        progress_t = text_colored("green", f"progress: {progress}%")
        logger.debug("Progress: %s%% %s", progress, progress_bar)
        logger.debug(progress_t)
