# encoding: utf-8

import logging_helper
from ..server.response import Response
from .shared import Shared

logging = logging_helper.setup_logging()


class RequestShared(Shared):

    def __init__(self,
                 *args,
                 **kwargs):

        super(RequestShared, self).__init__(*args,
                                            **kwargs)

        # Create the response object
        self.response = Response(request=self._request)

    # Error processing
    def _handle_error(self,
                      err,
                      status=500,  # Internal server error
                      log_msg=u'Something went wrong!',
                      exception=True):

        # Log the error
        self._log_error(err=err,
                        log_msg=log_msg,
                        exception=exception)

        # Setup error response
        self.response.generate_error(err=err,
                                     status=status)
