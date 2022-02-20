import logging
import sys
from logging import Logger


class LoggerFactory:
    @staticmethod
    def create(logger_name: str, logging_level: int = logging.INFO) -> Logger:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        logger = logging.getLogger(logger_name)

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging_level)

        return logger
