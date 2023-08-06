import logging


class SimpleInMemoryBackend:
    """
    Simple in memory backend, designed to simplify tests.
    """

    def __init__(self):
        self.messages = []

    def format(self, level, message):
        def level_name(level):
            if level == logging.INFO:
                return 'INFO'
            raise ValueError("Unknown level.")

        return '[{}] {}'.format(level_name(level), message)

    def info(self, message):
        self.messages.append(self.format(logging.INFO, message))

    def content(self):
        return '\n'.join(self.messages)

    def clear(self):
        self.messages = []

    def __len__(self):
        """
        Returns number of messages added.
        """
        return len(self.messages)


# Alias of logging
StandardBackend = logging