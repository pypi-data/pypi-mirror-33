class Logger:

    def __init__(self, logger_adapter):
        self.logger = logger_adapter

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def warn(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)
