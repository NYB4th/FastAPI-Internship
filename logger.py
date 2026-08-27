import logging
import sys

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logger(name: str = "fastapi_app") -> logging.Logger:
    """Configures and returns a single named logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOG_FORMAT)
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)

    return logger


logger = setup_logger()
