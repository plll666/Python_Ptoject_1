import logging

def make_logger(name: str) -> logging.Logger:
    """Создает и настраивает логгер с указанным именем"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger
