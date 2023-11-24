import logging
import os


def init_logger(name):
    path = 'logs'
    if os.path.split(os.getcwd())[-1] != 'twitter-campaign-manager':
        path = os.path.join('..', path)

    if not os.path.exists(path):
        os.makedirs(path)

    logging.basicConfig(filemode='a', level=logging.DEBUG)
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(os.path.join(path, f'{name}.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


class Logger:
    logger = init_logger('logger')
