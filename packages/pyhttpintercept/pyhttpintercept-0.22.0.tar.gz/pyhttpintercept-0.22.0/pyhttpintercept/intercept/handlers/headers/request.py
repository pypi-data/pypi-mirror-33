# encoding: utf-8

import logging_helper
from pyhttpintercept.intercept.handlers._base import BaseInterceptHandler
from pyhttpintercept.config.constants import HandlerTypeConstant

logging = logging_helper.setup_logging()


class InterceptHandler(BaseInterceptHandler):

    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        Called by HTTP_Web Server to modify a request.
        There should be no need to modify or override this.

        Filters modifiers so that only the ones appropriate
        to the message are applied.

        If there are no modifiers or a modifier fails to load,
        just returns empty lists.

        returns dict of inserts and deletes, each with list
        of key value pairs for the headers.

        It's up the to caller to apply the modifications
        """

        headers = {}

        if self.can_you_handle(request):  # Shouldn't need this check, but worth leaving in

            # apply all modifications:
            for modifier in modifiers:
                logging.debug(modifier)

                try:
                    if self._validate_modifier_type(modifier_type=HandlerTypeConstant.request_headers,
                                                    modifier=modifier):
                        headers.update(
                            modifier.module.modify(request=request,
                                                   response=response,
                                                   modifier=modifier))

                except KeyError as err:
                    logging.exception(err)
                    logging.warning(u'{modifier} modifier does '
                                    u'not exist for {module}'.format(modifier=modifier.modifier,
                                                                     module=modifier.handler))

                finally:
                    logging.debug(u'Modified Headers: {r}'.format(r=headers))

        headers = {k.lower(): v
                   for k, v in iter(headers.items())}

        return headers
