import logging


def set_logging_info_level_with_default_format():
    logging.basicConfig(
        level=logging.INFO,
        format=
        # '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
        '%(asctime)s [%(levelname)s] %(message)s',
        # datefmt='%a, %d %b %Y %H:%M:%S')
        datefmt='%d %b %Y %H:%M:%S')
