import logging
import os
import sys

from utils.arabic_display import display_text


def _resolve_level(default=logging.WARNING):
    raw = os.getenv("DZEXAMS_LOG_LEVEL", "").strip().upper()
    if not raw:
        return default
    return getattr(logging, raw, default)


def setup_logger(name="dzexams", level=None):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(_resolve_level() if level is None else level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    handler.addFilter(ArabicMessageFilter())
    logger.addHandler(handler)
    return logger


class ArabicMessageFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = display_text(record.msg)
        return True


log = setup_logger()
log.addFilter(ArabicMessageFilter())
