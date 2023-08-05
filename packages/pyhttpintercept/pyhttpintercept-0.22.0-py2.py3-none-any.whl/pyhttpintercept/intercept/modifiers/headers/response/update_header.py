# encoding: utf-8

u"""
============================================================
Modifies or adds to the received HTTP headers.
------------------------------------------------------------
Filter     : string to match in the request url
Override   : N/A
Parameters : Comma separated Key/Value pairs
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

        # Modify headers

        for key in modifier.params:
            logging.debug(key)
            modified_headers[key] = modifier.params[key]

        if modified_headers:
            logging.info(u'Modified headers: {h}'.format(h=modified_headers))

        else:
            logging.info(u'No headers modified')

    else:
        logging.debug(u'URL does not match header modification filter. No modifications made')

    return modified_headers
