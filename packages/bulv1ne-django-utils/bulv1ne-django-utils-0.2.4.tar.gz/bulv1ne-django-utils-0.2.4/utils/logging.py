import logging


class Logger():
    def __init__(self, **kwargs):
        self.options = kwargs
        self.logger = logging.getLogger(kwargs.get('name'))

    def copy(self, **kwargs):
        options = self.options.copy()
        options.update(kwargs)
        return Logger(**options)

    def construct_msg(self, msg):
        return ':'.join([
            '{}={}'.format(key, value)
            for key, value in self.options.get('fields', {}).items()
        ] + [str(msg)]
        )

    def name(self, name):
        return self.copy(name=name)

    def fields(self, **kwargs):
        return self.copy(fields=kwargs)

    def log(self, level, msg, *args, **kwargs):
        self.logger.log(level, self.construct_msg(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self.construct_msg(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(self.construct_msg(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self.construct_msg(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(self.construct_msg(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(self.construct_msg(msg), *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(self.construct_msg(msg), *args, **kwargs)


logger = Logger()


def getLogger(name):
    return Logger(name=name)
