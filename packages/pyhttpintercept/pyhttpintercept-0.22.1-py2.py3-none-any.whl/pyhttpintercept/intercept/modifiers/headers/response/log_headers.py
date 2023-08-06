# encoding: utf-8

u"""
============================================================
Logs received HTTP headers at Information level.
------------------------------------------------------------
Filter     : string to match in the request url
Override   : N/A
Parameters : header name or part of the header value
             leave blank to log all headers.
============================================================
"""

import logging_helper
from future.utils import iteritems
from pyhttpintercept.intercept.handlers.support import parse_list_parameters

logging = logging_helper.setup_logging()


def modify(request,
           response,
           modifier):

    if modifier.passes_filter(value=request,
                              wildcards=u'*'):

        log = logging_helper.LogLines(u'Response headers:')
        # Setup parameters
        parse_list_parameters(modifier)

        params = modifier.params

        for header, value in iter(response.headers.items()):
            if not params or header in params or any(p in value for p in params):
                log.append(u'"{header}":"{value}"'.format(header=header,
                                                          value=value))

    return {}
