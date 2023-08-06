import logging.config
from logging import getLogger
from clean.infra.log.utils.config import LOG_CONFIG

logging.config.dictConfig(LOG_CONFIG)
