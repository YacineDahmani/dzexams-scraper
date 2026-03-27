import logging
import sys

from utils.arabic_display import display_text


def setup_logger(name="dzexams", level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


class ArabicMessageFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = display_text(record.msg)
        return True


log = setup_logger()
log.addFilter(ArabicMessageFilter())
