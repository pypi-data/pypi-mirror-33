from functools import wraps
class LoggerAspect:
    def __init__(self, backend):
        self.backend = backend

    def make_message(self, message, *args, **kwargs):
        return str(message).format(*args, **kwargs)

    def make_log(self, log_maker, message):
        raise NotImplementedError

    def info(self, message):
        return self.make_log(self.backend.info, message)

    def debug(self, message):
        return self.make_log(self.backend.debug, message)

    def error(self, message):
        return self.make_log(self.backend.error, message)


class LoggerBefore(LoggerAspect):
    def make_log(self, log_maker, message):
        def advice(func):
            @wraps(func)
            def call(*args, **kwargs):
                log_maker(self.make_message(message, *args, **kwargs))
                return func(*args, **kwargs)

            return call

        return advice


class LoggerAfter(LoggerAspect):
    def make_log(self, log_maker, message):
        def advice(func):
            @wraps(func)
            def call(*args, **kwargs):
                result = func(*args, **kwargs)
                if isinstance(result, dict):
                    log_maker(self.make_message(message, **result))
                elif isinstance(result, (list, tuple)):
                    log_maker(self.make_message(message, *result))
                else:
                    log_maker(self.make_message(message, result))
                return result

            return call

        return advice