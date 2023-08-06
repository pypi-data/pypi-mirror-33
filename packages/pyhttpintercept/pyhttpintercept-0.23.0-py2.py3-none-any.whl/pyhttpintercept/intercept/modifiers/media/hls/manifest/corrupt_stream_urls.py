# encoding: utf-8

u"""
============================================================
 Corrupt HLS manifest stream URLs
------------------------------------------------------------
Filter     : string to match in the request url
Override   : N/A
Parameters : random: True/False if random is set then only
                some media URIs will be corrupted.
============================================================
"""

import random
import logging_helper
from pyhttpintercept.intercept.handlers.support import parse_dictionary_parameters

logging = logging_helper.setup_logging()


def modify(request,
           response,
           modifier):

    if not modifier.passes_filter(request):
        logging.debug(u'URL does not match manifest modification filter. No modifications made.')
        return response

    # Set up parameters
    parse_dictionary_parameters(modifier)

    logs = logging_helper.LogLines(level=logging_helper.DEBUG)

    # Modify

    # Get the file lines
    try:
        lines = response.content.splitlines()

    except Exception as err:
        logging.error(err)
        lines = []

    lines = [line for line in lines if line]
    logging.debug(lines)

    if lines and lines[0] != u'#EXTM3U':
        logging.error(u'playlist error -> #EXTM3U tag missing. No modifications made.')
        return response

    for idx, line in enumerate(lines):
        if line.startswith(u'#EXT'):
            if line.startswith(u'#EXTINF'):
                # #EXTINF:<duration_seconds>,[<title>]
                # <Any other media segment tags>
                # < URI >

                if len(lines) > idx + 1:
                    corrupt = (random.choice([True, True, False, False, False])
                               if modifier.params.get(u'random', False)
                               else True)

                    if corrupt:
                        lines[idx + 1] = u'corrupt_{line}'.format(line=lines[idx + 1])
                        logging.info(u'Corrupting line, updating to: {line}'.format(line=lines[idx + 1]))

    response._content = u'\n'.join(lines)

    logs.append(u'HLS Playlist:')
    logs.append(lines)
    logs.push()

    return response
