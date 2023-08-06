import logging

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)
logger = logging.getLogger('dxl')


def set_logging_level(level=logging.INFO):
    logger.setLevel(level)


__all__ = ['logger', 'set_logging_level']
