# -*- coding: utf-8 -*-
"""module qatestlink.core.utils.logger_manager"""


import logging


class LoggerManager(object):
    """
    Start logger named 'qatestlink'
     with DEBUG level and just with console reporting
    """

    log = None

    def __init__(self, log_level=None):
        """Start logger"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('qatestlink')
        logger_stream = logging.StreamHandler()
        if log_level is None or log_level == 'DEBUG':
            log_level = logging.DEBUG
        elif log_level == 'INFO':
            log_level = logging.INFO
        elif log_level == 'WARNING':
            log_level = logging.WARNING
        elif log_level == 'ERROR':
            log_level = logging.ERROR
        elif log_level == 'CRITICAL':
            log_level = logging.CRITICAL
        logger.setLevel(log_level)
        logger_stream.setLevel(log_level)
        logger_stream.setFormatter(formatter)
        for old_handler in logger.handlers:
            logger.removeHandler(old_handler)
        logger.addHandler(logger_stream)
        # alias to improve logging calls
        self.log = logger
