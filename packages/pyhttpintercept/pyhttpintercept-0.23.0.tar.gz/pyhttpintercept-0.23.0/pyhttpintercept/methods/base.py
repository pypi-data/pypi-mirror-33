# encoding: utf-8

import socket
import requests
import logging_helper
from ..server.response import Response
from ..redirect import RedirectRequest
from ..hosting import HostRequest
from ..intercept import InterceptRequest
from ..exceptions import CircularReference
from .request_shared import RequestShared

logging = logging_helper.setup_logging()


class BaseRequestHandler(RequestShared):

    METHOD_TYPE = None  # This should be set by inheriting class

    def __init__(self,
                 scenarios=None,
                 *args,
                 **kwargs):

        super(BaseRequestHandler, self).__init__(*args,
                                                 **kwargs)

        self._scenarios = scenarios

        logging.info(self.prefix_message(u'Original URI: {uri}'.format(uri=self.request_uri)))
        logging.debug(self.prefix_message(u'Original Headers: {h}'.format(h=self.request_headers)))
        logging.debug(self.prefix_message(u'Client Address: {a}'.format(a=self.client_address)))

        # Processing parameters
        self.retrieved_headers = {}
        self.modified_headers = {}

        # handler flags
        self.redirected = False
        self.hosted = False
        self.intercepted = False
        self.proxied = False

    def extract_parameters(self):
        self._request.parameters = {}

    # Interface
    def handle(self):

        logging.debug(self._get_debug_separator(u'HANDLE REQUEST'))

        try:
            self.extract_parameters()

            self.__redirect_request()

            # Attempt to host the request
            self.__host_request()

            if not self.hosted:
                # Attempt to intercept the request only if not already hosted
                self.__intercept_request()

            if not self.hosted and not self.intercepted:
                # Attempt to proxy the request only if not already hosted or intercepted
                self.__proxy_request()

        except CircularReference as err:
            self._handle_error(err=err,
                               status=400,
                               log_msg=str(err))

        except requests.exceptions.RequestException as err:
            self._handle_error(err=err,
                               status=408,  # Request Timeout  # TODO: Careful this might not always be a timeout!
                               log_msg=u'Request to {url} failed'.format(url=self.request_uri))

        except socket.error as err:
            self._request.close_connection = 1  # Stop any further connections as we have a socket error
            self._log_error(err=err,
                            exception=False)

        except Exception as err:
            self._handle_error(err=err)  # Uses default status - 500: Internal server error

        finally:

            # Reply to client with response (Exception handling within respond method)
            logging.debug(self._get_debug_separator(u'RESPOND'))
            self.response.respond()

        logging.debug(self._get_debug_separator(u'DONE'))

    # Request handlers  TODO: Wildcard support
    # Redirect
    def __redirect_request(self):

        redirect = RedirectRequest(request=self._request,
                                   uri=self.request_uri)

        self.response, self.redirected = redirect.redirect_request()

        if self.redirected:
            self.request_uri = redirect.request_uri

    # Hosting
    def __host_request(self):

        # Only host the request when it is addressed directly to the server
        if self._addressed_to_self:
            host = HostRequest(request=self._request,
                               uri=self.request_uri)

            # TODO: should we be setting response if hosted comes back False?
            self.response, self.hosted = host.host_request()

        else:
            pass
            # logging.debug(self.prefix_message(u'Not Hosting this request, Request not addressed to this server.'))

    # Intercept
    def __intercept_request(self):

        if self._scenarios is not None:
            intercept = InterceptRequest(request=self._request,
                                         scenarios=self._scenarios,
                                         uri=self.request_uri)

            # TODO: should we be setting response if intercepted comes back False?
            self.response, self.intercepted = intercept.intercept_request()

        else:
            logging.warning(self.prefix_message(u'Intercept is disabled as self._scenarios is None!'))

    # Proxy TODO
    # TODO: Is this not just intercept without the any active modifications?
    def __proxy_request(self):

        # TODO: Check for configured proxy
        proxy = False

        if proxy:
            # Get real response from server
            response = requests.get(url=self.request_uri,
                                    timeout=1.5)
            # TODO: need to forward headers & query params also!

            # Prepare response
            self.response = Response(request=self._request,
                                     uri=self.request_uri,
                                     response=response)
            self.response.prepare_headers()
