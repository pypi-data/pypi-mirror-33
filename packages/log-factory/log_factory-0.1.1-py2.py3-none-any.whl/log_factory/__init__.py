import logging
import argparse

root_logger = logging.getLogger('')
default_fmt = '%(asctime)s %(name)s %(levelname)s| %(message)s'

logging_parser = argparse.ArgumentParser(add_help=False)
logging_parser.add_argument('-v', '--verbose', dest='verbose',
                            action='store_true',
                            help='Enable debug logging')
logging_parser.add_argument('-l', '--log-file', dest='logfile',
                            help='Enable debug logging')


def create(fmt=default_fmt):
    stream_formatter = \
        logging.Formatter(fmt)

    root_logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(stream_formatter)
    ch.propagate = False

    root_logger.addHandler(ch)


def set_log_level(lvl):
    for handler in root_logger.handlers:
        if isinstance(root_logger.handlers[0], logging.StreamHandler):
            handler.setLevel(lvl)


def add_file_handler(filename, fmt=default_fmt, lvl=logging.INFO):
    file_formatter = \
        logging.Formatter(fmt)

    fh = logging.FileHandler(filename, mode='w')
    fh.setLevel(lvl)
    fh.setFormatter(file_formatter)
    fh.propagate = False

    root_logger.addHandler(fh)


def get_logger(name=''):
    return logging.getLogger(name)
