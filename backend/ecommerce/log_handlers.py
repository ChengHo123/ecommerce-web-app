"""
Custom logging handlers, formatters, and filters.
"""
import logging
import logging.handlers
import traceback


# ── Noise filter ───────────────────────────────────────────────────────────

_IGNORED_404_PATHS = (
    "/.well-known/",
    "/favicon.ico",
    "/apple-touch-icon",
    "/robots.txt",
    "/sitemap.xml",
)


class IgnoreNoise404(logging.Filter):
    """Drop browser auto-probe 404s from error.log."""
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for path in _IGNORED_404_PATHS:
            if path in msg:
                return False
        return True


# ── Rich formatter (for error.log) ────────────────────────────────────────

_SEP_WIDE = "═" * 62
_SEP_THIN = "─" * 62
_LEVEL_ICON = {
    "DEBUG":    "🔍 DEBUG",
    "INFO":     "ℹ  INFO ",
    "WARNING":  "⚠  WARN ",
    "ERROR":    "✖  ERROR",
    "CRITICAL": "💀 CRIT ",
}


class RichFormatter(logging.Formatter):
    """
    Multi-line formatter that includes:
      - Level + timestamp header
      - Full message
      - HTTP request context (method, URL, IP, user, user-agent)
        when the record comes from django.request / django.server
      - Full traceback when exc_info is set
      - Extra fields attached via logger.xxx(..., extra={...})

    Used for error.log so every entry is self-contained and debuggable.
    """

    def format(self, record: logging.LogRecord) -> str:
        icon = _LEVEL_ICON.get(record.levelname, record.levelname)
        ts   = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        lines = [
            "",
            f"╔══ {icon} ══ {ts} ══ {record.name}",
            f"║  {record.getMessage()}",
        ]

        # ── HTTP request context ──────────────────────────────────────
        req = getattr(record, "request", None)
        if req is not None:
            try:
                method  = req.method
                url     = req.build_absolute_uri()
                ip      = (
                    req.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                    or req.META.get("REMOTE_ADDR", "?")
                )
                agent   = req.META.get("HTTP_USER_AGENT", "—")[:120]
                user    = req.user
                user_str = (
                    f"{user.name} (pk={user.pk})"
                    if getattr(user, "is_authenticated", False)
                    else "anonymous"
                )
                lines += [
                    f"║  {'Method':8}: {method}",
                    f"║  {'URL':8}: {url}",
                    f"║  {'IP':8}: {ip}",
                    f"║  {'User':8}: {user_str}",
                    f"║  {'Agent':8}: {agent}",
                ]
            except Exception:
                pass

        # ── Extra fields (from logger.xxx(..., extra={...})) ──────────
        _std = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "taskName",
            "message", "asctime", "request", "status_code",
        }
        for k, v in record.__dict__.items():
            if k.startswith("_") or k in _std:
                continue
            lines.append(f"║  {k:8}: {v}")

        # ── Traceback ─────────────────────────────────────────────────
        if record.exc_info and record.exc_info[0] is not None:
            lines.append(f"║  {_SEP_THIN}")
            tb = traceback.format_exception(*record.exc_info)
            for tb_line in "".join(tb).rstrip().splitlines():
                lines.append(f"║  {tb_line}")
        elif record.exc_text:
            lines.append(f"║  {_SEP_THIN}")
            for tb_line in record.exc_text.rstrip().splitlines():
                lines.append(f"║  {tb_line}")

        lines.append(f"╚{'═' * 62}")
        return "\n".join(lines)


# ── Handler factory ────────────────────────────────────────────────────────

def make_timed_handler(
    filename: str,
    backup_count: int = 30,
    formatter: str = "verbose",
    level: str = "DEBUG",
) -> logging.handlers.TimedRotatingFileHandler:
    """
    Factory for TimedRotatingFileHandler called by Django's dictConfig.
    Rotated files are renamed to  <filename>.YYYY-MM-DD.
    """
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=filename,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
        delay=True,
        utc=False,
    )
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(getattr(logging, level.upper(), logging.DEBUG))
    return handler
