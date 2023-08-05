# encoding: utf-8

import socket
import logging_helper
from threading import currentThread
from http.server import BaseHTTPRequestHandler
from classutils.decorators import profiling
from ..methods.get import GetHandler
from ..methods.post import PostHandler
from .._constants import PROFILER_PROFILE_ID

logging = logging_helper.setup_logging()


class RequestHandler(BaseHTTPRequestHandler, object):
    BaseHTTPRequestHandler.protocol_version = u"HTTP/1.1"

    #  Override base class logging function
    def log_message(self,
                    fmt,
                    *args):
        logging.info(u"{t}: {addr} - {fmt}".format(t=self.thread,
                                                   addr=self.client_address[0],
                                                   fmt=fmt % args))

    @property
    def thread(self):
        thread = currentThread().name
        return thread if thread else u'?'

    # Request handlers
    @profiling.profile(profile_id=PROFILER_PROFILE_ID)
    def do_GET(self):
        GetHandler(request=self,
                   scenarios=self.server.scenarios).handle()

    @profiling.profile(profile_id=PROFILER_PROFILE_ID)
    def do_POST(self):
        PostHandler(request=self,
                    scenarios=self.server.scenarios).handle()

    # Need to add try/catch for broken pipe socket errors in inherited methods!
    def handle(self):

        # Register this request as an open request
        self.server.open_requests.append(self)

        try:
            super(RequestHandler, self).handle()

        except socket.error as err:
            self.close_connection = 1  # Stop any further connections as we have a socket error
            logging.error(u'{t}: HTTPRequestHandler.handle error: {err}'.format(t=self.thread,
                                                                                err=err))

        except Exception as err:
            logging.exception(u'{t}: HTTPRequestHandler.handle unknown error: {err}'.format(t=self.thread,
                                                                                            err=err))

    def finish(self):

        try:
            super(RequestHandler, self).finish()

        except socket.error as err:
            logging.error(u'{t}: HTTPRequestHandler.finish error: {err}'.format(t=self.thread,
                                                                                err=err))

            try:
                if not self.rfile.closed:
                    self.rfile.close()

            except socket.error as err:
                logging.error(u'{t}: HTTPRequestHandler.finish rfile error: {err}'.format(t=self.thread,
                                                                                          err=err))

            except Exception as err:
                logging.exception(u'{t}: HTTPRequestHandler.finish rfile unknown error: {err}'.format(t=self.thread,
                                                                                                      err=err))

        except Exception as err:
            logging.exception(u'{t}: HTTPRequestHandler.finish unknown error: {err}'.format(t=self.thread,
                                                                                            err=err))

        # UnRegister this request as an open request
        idx = self.server.open_requests.index(self)
        del self.server.open_requests[idx]
