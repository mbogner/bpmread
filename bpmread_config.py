import os


class Config:
    APP_NAME = os.environ.get('APP_NAME', 'bpmread')
    APP_ENVIRONMENT = os.environ.get('APP_ENVIRONMENT', 'dev')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    DEFAULT_ENCODING = 'utf-8'

    # LOGGING
    # --------------------------------------------------------------------------
    # possible: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = os.environ.get(
        'LOG_FORMAT',
        '%(asctime)s %(levelname)s [%(threadName)s,%(name)s] %(filename)s:%(lineno)d - %(message)s'
    )
