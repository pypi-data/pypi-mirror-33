import logging, logging.config
from logging import getLoggerClass, addLevelName, setLoggerClass, NOTSET
import os
import json
from typing import Any, Dict, Tuple

from tornado.web import RequestHandler

def setup_logging \
(
    default_path='configs/logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Setup logging configuration
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
    
    def trace(self, message, *args, **kwargs):
        self.log(TRACE_LEVEL_NUM, message, *args, **kwargs)
    
    def develop(self, message, *args, **kwargs):
        self.log(DEVELOP_LEVEL_NUM, message, *args, **kwargs)

setLoggerClass(ExtendedLogger)

class BraceString(str):
    kwargs: Dict[str, Any] = {}
    def __mod__(self, other):
        return self.format(*other, **self.kwargs)
    def __str__(self):
        return self

class StyleAdapter(logging.LoggerAdapter):
    
    default_style: str
    def __init__(self, logger: logging.Logger, extra=None, *, style='%'):
        super(StyleAdapter, self).__init__(logger, extra)
        self.default_style = style
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        if (kwargs.pop('style', self.default_style) == "{"):
            msg = BraceString(msg)
            msg.kwargs = kwargs
        return msg, kwargs
