import multiprocessing
import logging
import os

# from concurrent_log_handler import ConcurrentRotatingFileHandler

LOGLEVEL = logging.INFO


def get_logger():
    
    formatter = logging.Formatter(
        "%(asctime)s - %(module)s - %(levelname)s - %(message)s [Process: %(process)d, %(filename)s:%(funcName)s(%(lineno)d)]"
    )
    
    # logger = logging.getLogger()
    logger = multiprocessing.get_logger()


    if logger.handlers:
        return logger

    # Use an absolute path to prevent file rotation trouble.
    logfile = os.path.abspath("logs.log")

    logger.setLevel(LOGLEVEL)

    # Rotate log after reaching 512K, keep 5 old copies.
    # filehandler = ConcurrentRotatingFileHandler(
    #     logfile, mode="a", maxBytes=512 * 1024, backupCount=5, encoding="utf-8"
    # )
    filehandler = logging.FileHandler('logs/simulation.log')

    filehandler.setLevel(LOGLEVEL)
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

        # ch = logging.StreamHandler()
    # ch.setLevel(LOGLEVEL)
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)


    return logger


def __create_logger():
    import multiprocessing, logging
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(\
        '[%(asctime)s| %(levelname)s| %(processName)s] %(message)s')
    handler = logging.FileHandler('logs/your_file_name.log')
    handler.setFormatter(formatter)

    # this bit will make sure you won't have 
    # duplicated messages in the output
    if not len(logger.handlers): 
        logger.addHandler(handler)
    return logger
