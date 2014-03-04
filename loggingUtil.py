#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2013 Nippon Telegraph and Telephone Corporation.
# All rights reserved.
import logging
import logging.config
import functools
import sys
import os

DEFAULT_PROP_PATH = os.path.dirname(os.path.abspath(__file__)) + "/logging.conf"

class LoggingUtil(object):

    # デフォルトプロパティファイルパス(利用に合わせ設定すること)
    
    logging.config.fileConfig(DEFAULT_PROP_PATH)
    logger = logging.getLogger('top.mid')

    debug = functools.partial(logger.debug)
    info = functools.partial(logger.info)
    warn = functools.partial(logger.warning)
    error = functools.partial(logger.error)
    critical = functools.partial(logger.critical)
    exception = functools.partial(logger.exception)

    @classmethod
    def accessDecolator(cls,f):
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            cls.info('start ' + f.__name__)
            cls.info('input parameter ' + str(args) + str(kwds))
            f(*args, **kwds)
            cls.info('exit ' + f.__name__)
        return wrapper


    @classmethod
    def getLogger(cls):
        return cls.logger


def _main():
    if len(sys.argv) != 3:
        return 0

    loglevel = sys.argv[1]
    logMessage = sys.argv[2]
    
    logger = loggingUtil()
    if 'debug' == loglevel:
        logger.debug(logMessage)
    elif 'info' == loglevel:
        logger.info(logMessage)
    elif 'warn' == loglevel:
        logger.warn(logMessage)
    elif 'error' == loglevel:
        logger.error(logMessage)
    elif 'critical' == loglevel:
        logger.critical(logMessage)

    return 0
    
    
if __name__ == '__main__':
    sys.exit(_main())
