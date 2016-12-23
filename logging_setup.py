import logging
import os


def setup_logger(name):
    # ensure access to the folder where the logs are kept
    folder = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(folder):
        os.makedirs(folder)

    # setup the format for the logger
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # makes a logger with the passed name (most likely a module name)
    logger = logging.getLogger(name)

    # setup the handler (this sends the logs to the file with the given formatter)
    handler = logging.FileHandler(os.path.join(folder, name + ".log"))
    handler.setFormatter(formatter)

    # finalize the logger by adding the handler and setting the logging level
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
