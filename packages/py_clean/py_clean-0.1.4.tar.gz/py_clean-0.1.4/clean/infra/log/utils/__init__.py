import logging
try:
    from settings import DEBUG
except ImportError:
    DEBUG = True
from raven.handlers.logging import SentryHandler
from clean.infra.log.utils.colors import color_style


class RequireDebugFalse(logging.Filter):
    def filter(self, record):
        return not DEBUG


class RequireDebugTrue(logging.Filter):
    def filter(self, record):
        return DEBUG


class ColorsFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(ColorsFormatter, self).__init__(*args, **kwargs)
        self.style = self.configure_style(color_style())

    def configure_style(self, style):
        style.DEBUG = style.HTTP_NOT_MODIFIED
        style.INFO = style.HTTP_INFO
        style.WARNING = style.HTTP_NOT_FOUND
        style.ERROR = style.ERROR
        style.CRITICAL = style.HTTP_SERVER_ERROR
        return style

    def format(self, record):
        message = logging.Formatter.format(self, record)
        colorizer = getattr(self.style, record.levelname, self.style.HTTP_SUCCESS)
        return colorizer(message)


class CaptureError(SentryHandler):

    def emit(self, record):
        return super(CaptureError, self).emit(record)
