# encoding: utf-8

import logging_helper
from ._base import BaseInterceptHandler

logging = logging_helper.setup_logging()


class InterceptHandler(BaseInterceptHandler):

    HANDLES_ERRORS = True

    def can_handle_status_code(self,
                               status_code):
        test = 200 <= status_code <= 400 or self.HANDLES_ERRORS
        logging.debug(u'200 <= status_code <= 400 or self.HANDLES_ERRORS: {test}'.format(test=test))
        return test

    @staticmethod
    def modify_body(request,
                    response,
                    modifier):

        try:
            response = modifier.module.modify(request=request,
                                              response=response,
                                              modifier=modifier)

            logging.debug(u'Modified response: {r}'.format(r=response))

        except Exception as e:
            logging.exception(e)
            logging.exception(u'Modifying failed:'
                              u'\n    handler   : {handler}'  # TODO: This can be replaced with unicode(modifier) 
                              u'\n    modifier  : {modifier}'
                              u'\n    filter    : {filter}'
                              u'\n    override  : {override}'
                              u'\n    parameters: {parameters}'.format(handler=modifier.handler,
                                                                       modifier=modifier.modifier,
                                                                       filter=modifier.filter,
                                                                       override=modifier.override,
                                                                       parameters=modifier.params,
                                                                       module=modifier.module))
        return response

    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        Called by HTTP_Web Server to modify the body of a response.
        There should be no need to modify or override this.

        Filters modifiers so that only the ones appropriate
        to the message are applied.

        If there are no modifiers or a modifier fails to load,
        just returns the original response.

        Does not modify if can_handle_status_code is False.
        """

        # logging.debug(u'in {name}.handle_request'.format(name=self.__class__.__name__))

        if self.can_you_handle(request):  # Shouldn't need this check,  but worth leaving in

            if self.can_handle_status_code(response.status_code):
                # apply all modifications:
                for modifier in modifiers:
                    try:
                        response = self.modify_body(request=request,
                                                    response=response,
                                                    modifier=modifier)

                    except KeyError as err:
                        logging.exception(err)
                        logging.warning(u'{modifier} modifier does '
                                        u'not exist for {module}'.format(modifier=modifier.modifier,
                                                                         module=modifier.handler))
            else:
                logging.debug(u'Not running modifiers. Cannot handle status code {sc}'
                              .format(sc=response.status_code))

        return response
