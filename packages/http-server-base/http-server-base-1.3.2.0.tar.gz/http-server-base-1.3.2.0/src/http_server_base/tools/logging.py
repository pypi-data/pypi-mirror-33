import logging, logging.config
from logging import getLoggerClass, addLevelName, setLoggerClass, NOTSET
import os
import json

def setup_logging \
(
    default_path='configs/logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

TRACE_LEVEL_NUM = 5
DEVELOP_LEVEL_NUM = 60

class ExtendedLogger(getLoggerClass()):
    def __init__(self, name, level=NOTSET):
        super().__init__(name, level)

        addLevelName(TRACE_LEVEL_NUM, "TRACE")
        addLevelName(DEVELOP_LEVEL_NUM, "DEVELOP")
        
    def trace(self, message, *args, **kws):
        if (self.isEnabledFor(TRACE_LEVEL_NUM)):
            # args are sent as an argument
            self._log(TRACE_LEVEL_NUM, message, args, **kws)

    def develop(self, message, *args, **kws):
        if (self.isEnabledFor(DEVELOP_LEVEL_NUM)):
            # args are sent as an argument
            self._log(DEVELOP_LEVEL_NUM, message, args, **kws)


setLoggerClass(ExtendedLogger)
