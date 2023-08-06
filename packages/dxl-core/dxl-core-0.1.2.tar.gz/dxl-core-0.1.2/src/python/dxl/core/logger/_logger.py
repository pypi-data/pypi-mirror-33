from .aspect import LoggerBefore, LoggerAfter
import logging


class Logger:
    def __init__(self, name_or_backend):
        """
        If name_or_backend is str, 
        use default backend logging.getLogger(name_or_backend).

        Backend should have methods:
        `b.info`, `b.debug`, `b.error`, `b.warning`, etc.
        """
        if isinstance(name_or_backend, str):
            self.backend = logging.getLogger(name_or_backend)
        else:
            self.backend = name_or_backend
        self.before_aspect = LoggerBefore(self.backend)
        self.after_aspect = LoggerAfter(self.backend)

    @property
    def before(self):
        return self.before_aspect

    @property
    def after(self):
        return self.after_aspect

    def info(self, message):
        self.backend.info(message)
