# encoding: utf-8

u"""
============================================================
[TBD] Removes request headers
------------------------------------------------------------
Filter     : string to match in the request url
Override   : N/A
Parameters : Comma separated list of headers
============================================================
"""

import logging_helper
from pyhttpintercept.intercept.handlers.support import parse_dictionary_parameters

logging = logging_helper.setup_logging()


def modify(request,
           response,
           modifier):

    modified_headers = {}

    if modifier.passes_filter(request):
        # Set up parameters
        parse_dictionary_parameters(modifier)

        logs = logging_helper.LogLines()

        # Modify headers

        for key in modifier.params:
            modified_headers[key] = None
            logs.append(u'Marked header for removal: {h}'.format(h=key))

        if not modified_headers:
            logs.append(u'No headers marked for modification')

    else:
        logging.debug(u'URL does not match header modification filter. No modifications made')

    return modified_headers
