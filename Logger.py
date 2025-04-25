from loguru import logger
import sys

class Logger:
    def __init__(self, log_file: str = "app.log", level: str = "INFO"):
        logger.remove()
        log_format = (
            "<cyan>{time:YYYY-MM-DD HH:mm:ss}</cyan> | "
            "<level>{level: <8}</level> | "
            "<magenta>{module}:{function}:{line}</magenta> - "
            "<level>{message}</level>"
        )
        logger.add(sys.stdout, level=level, colorize=True, format=log_format, backtrace=True, diagnose=True)
        logger.add(log_file, level=level, format="{time} | {level} | {message}", rotation="500 MB", compression="zip")

    def info(self, message: str):
        logger.opt(depth=1).info(message)

    def warning(self, message: str):
        logger.opt(depth=1).warning(message)

    def error(self, message: str):
        logger.opt(depth=1).error(message)

    def debug(self, message: str):
        logger.opt(depth=1).debug(message)

    def critical(self, message: str):
        logger.opt(depth=1).critical(message)
