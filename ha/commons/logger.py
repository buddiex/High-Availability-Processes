import logging
import config as conf


def get_module_logger(mod_name ):
    logger = logging.getLogger(mod_name)
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-10s {} [%(filename)s:%(lineno)d] %(message)s'.format(''),
                                  datefmt='%d-%m-%Y:%H:%M:%S')

    fileHandler = logging.FileHandler("{0}.log".format(conf.LOG))
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if conf.DEBUG_MODE else logging.INFO)

    return logger
