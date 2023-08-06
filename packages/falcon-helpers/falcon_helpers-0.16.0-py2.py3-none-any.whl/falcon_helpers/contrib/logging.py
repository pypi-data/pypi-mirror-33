import logging


class Logging:

    def __init__(self, level=logging.INFO, fmt=None):
        self.log_level = level
        self.fmt = fmt or '[%(levelname)s] %(asctime)s - %(msg)s'

    def add_logger(self, name, handler, fmt=None, formatter=None, level=None):
        formatter = (
            logging.Formatter(fmt) if (fmt is not None and not formatter)
            else formatter if formatter
            else logging.Formatter(self.fmt)
        )

        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(level or self.log_level)
