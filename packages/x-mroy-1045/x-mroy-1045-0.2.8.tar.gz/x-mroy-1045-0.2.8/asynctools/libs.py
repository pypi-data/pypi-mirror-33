import logging

LOG_LEVEL=logging.ERROR

def loger(level=LOG_LEVEL):
    logging.basicConfig(level=level)
    return logging.getLogger(__file__)
