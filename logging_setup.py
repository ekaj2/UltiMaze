import logging
import os


def setup_logger(name):
    folder = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(folder):
        os.makedirs(folder)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    handler = logging.FileHandler("{folder}{name}.log".format(name=name, folder=folder))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
