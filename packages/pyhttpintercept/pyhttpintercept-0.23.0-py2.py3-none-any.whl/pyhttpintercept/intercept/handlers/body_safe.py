# encoding: utf-8

import logging_helper
from .body import InterceptHandler as BodyInterceptHandler

logging = logging_helper.setup_logging()


class InterceptHandler(BodyInterceptHandler):
    HANDLES_ERRORS = False
