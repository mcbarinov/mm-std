import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog
from structlog.typing import Processor


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


def configure_structlog(json_logs: bool = False, log_level: str = "DEBUG", compact: bool = False) -> None:
    timestamper: Processor = structlog.processors.TimeStamper(fmt="%H:%M:%S" if compact else "[%Y-%m-%d %H:%M:%S.%f]")

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        # Format the exception only for JSON logs, as we want to pretty-print them when
        # using the ConsoleRenderer
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=shared_processors  # noqa: RUF005
        + [
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: Processor
    log_renderer = structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()

    formatter: structlog.stdlib.ProcessorFormatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger: logging.Logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())
