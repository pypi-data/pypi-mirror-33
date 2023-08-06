try:
    from settings import SENTRY_DSN
except ImportError:
    SENTRY_DSN = ''


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'v': {
            'format': '%(levelname)s %(message)s'
        },
        "vv": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        'vvv': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'easy': {
            '()': 'clean.infra.log.utils.ColorsFormatter',
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '[%d/%b/%Y %H:%M:%S]'
        }
    },
    "filters": {
        "require_debug_false": {
            "()": "clean.infra.log.utils.RequireDebugFalse"
        },
        "require_debug_true": {
            "()": "clean.infra.log.utils.RequireDebugTrue"
        }
    },
    "handlers": {
        "console": {
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "easy",
            "stream": "ext://sys.stdout"
        },
        "server": {
            "filters": ["require_debug_false"],
            "class": "logging.StreamHandler",
            "formatter": "easy",
            "stream": "ext://sys.stdout"
        },
        'sentry': {
            'level': 'ERROR',
            "filters": ["require_debug_false"],
            "formatter": "easy",
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
        },
    },
    "loggers": {
        "app": {
            "level": 'DEBUG',
            "handlers": ["console"],
            "propagate": False
        },
        "app.serve": {
            "level": 'INFO',
            "handlers": ["server", "sentry"],
            "propagate": True
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"]
    }
}
