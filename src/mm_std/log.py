import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler


class ExtraFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in logging.LogRecord.__dict__
            and key
            not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "taskName",
                "asctime",
            )
        }
        if extras:
            extras_str = " | " + " ".join(f"{k}={v}" for k, v in extras.items())
            return base + extras_str
        return base


def configure_logging(developer_console: bool = False, console_level: int = logging.INFO) -> None:
    """
    Configure the root logger with a custom formatter that includes extra fields.
    """
    logger = logging.getLogger()
    logger.setLevel(console_level)
    logger.handlers.clear()

    console_handler: logging.Handler

    if developer_console:
        console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)
        formatter = ExtraFormatter("{message}", style="{")
    else:
        console_handler = logging.StreamHandler()
        formatter = ExtraFormatter("{asctime} - {name} - {levelname} - {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)


def init_logger(name: str, file_path: str | None = None, file_mkdir: bool = True, level: int = logging.DEBUG) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(level)
    log.propagate = False
    fmt = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(fmt)
    log.addHandler(console_handler)
    if file_path:
        if file_mkdir:
            Path(file_path).parent.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(file_path, maxBytes=10 * 1024 * 1024, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(fmt)
        log.addHandler(file_handler)
    return log
