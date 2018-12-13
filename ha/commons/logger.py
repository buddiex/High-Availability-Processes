import logging
import config as conf


def get_module_logger(mod_name ):
    logger = logging.getLogger(mod_name)
    formatter = logging.Formatter(' --- %(asctime)s,%(msecs)-4d %(threadName)-40s thread %(levelname)-6s {} %(filename)s:%(lineno)-1d >>> %(message)s'.format(''),
                                  datefmt='%d-%m-%Y:%H:%M:%S')

    fileHandler = logging.FileHandler("{0}.log".format(conf.LOG))
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    # handler = logging.StreamHandler()
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if conf.DEBUG_MODE else logging.INFO)

    return logger
