"""日志初始化与格式配置。"""

from __future__ import annotations

import logging
import sys

from .settings import AppSettings


class TraceIdFilter(logging.Filter):
    """为日志记录注入 trace_id 字段，便于请求级追踪。"""

    def filter(self, record: logging.LogRecord) -> bool:
        trace_id = "-"
        try:
            from .tracing import get_trace_id

            current_trace_id = get_trace_id()
            if current_trace_id:
                trace_id = current_trace_id
        except Exception:
            # 追踪上下文异常不应影响业务日志输出
            trace_id = "-"

        record.trace_id = trace_id
        return True


def _build_formatter(structured_logging: bool) -> logging.Formatter:
    """按配置构建日志格式。"""
    if structured_logging:
        return logging.Formatter(
            '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","trace_id":"%(trace_id)s","msg":"%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    return logging.Formatter(
        "\n%(asctime)s | %(levelname)-8s | %(name)s | trace=%(trace_id)s\n"
        "  └─ %(message)s",
        datefmt="%H:%M:%S",
    )


def configure_logging(settings: AppSettings) -> logging.Logger:
    """配置全局日志并返回根日志器。"""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)
    console_handler.setFormatter(_build_formatter(settings.structured_logging))
    console_handler.addFilter(TraceIdFilter())

    root_logger.addHandler(console_handler)

    try:
        from logging.handlers import RotatingFileHandler

        log_dir = settings.logs_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "redink.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(settings.log_level)
        file_handler.setFormatter(_build_formatter(settings.structured_logging))
        file_handler.addFilter(TraceIdFilter())
        root_logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Failed to setup file logging: {e}\n")

    logging.getLogger("backend").setLevel(settings.log_level)
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return root_logger
