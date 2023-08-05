# encoding: utf-8

u"""
============================================================
 Set target duration less than segment durations making
 the segment durations invalid.
------------------------------------------------------------
Filter     : string to match in the request url
Override   : N/A
Parameters : Target duration in seconds (int)
============================================================
"""

import logging_helper
from pyhttpintercept.config.constants import ModifierConstant

logging = logging_helper.setup_logging()


def modify(request,
           response,
           modifier):

    if not modifier.passes_filter(request):
        logging.debug(u'URL does not match manifest modification filter. No modifications made.')
        return response

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
        if line.startswith(u'#EXT-X-TARGETDURATION'):
            # #EXT-X-TARGETDURATION:<duration_seconds>

            target_duration = modifier.get(ModifierConstant.params)

            if target_duration is not None:
                lines[idx] = u'#EXT-X-TARGETDURATION:{duration}'.format(duration=target_duration)
                logging.info(u'Target duration updated to: {dur}'.format(dur=target_duration))

    logging.debug(lines)

    response._content = u'\n'.join(lines)

    return response
