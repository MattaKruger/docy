import logging
import os
import sys
from datetime import datetime

os.makedirs("logs", exist_ok=True)


def setup_logger(name: str, level: int = logging.INFO):
    """Set up a logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    log_file = f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


main_logger = setup_logger("main")
github_logger = setup_logger("github")
chroma_logger = setup_logger("chroma")
