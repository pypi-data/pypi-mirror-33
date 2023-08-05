# encoding: utf-8

# Based on https://github.com/Dejvino/https-multiplexer/blob/master/multiplexer.py

import time
import socket
import logging_helper
from select import select
from threading import currentThread, Thread
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from timingsutil import Timeout

logging = logging_helper.setup_logging()

# following method names are defined in the HTTP protocol
HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "TRACE", "OPTIONS", "CONNECT", "PATCH"]
DEFAULT_DESTINATION = ('127.0.0.1', 80)


class MultiplexServer(object):

    def __init__(self,
                 server_address,
                 destination_address,
                 destination_https_port=443,
                 threads=cpu_count(),
                 # request_threads is probably excessive however when keep-alive is set on
                 # a request the thread is consumed until the connection gets closed!
                 request_threads=200,
                 threading=True):

        """Constructor.  May be extended, do not override."""

        self.server_address = server_address
        self.destination_address = destination_address

        self.multiplex_port = server_address[-1]
        self.http_port = destination_address[-1]
        self.https_port = destination_https_port

        self._threading = threading  # Denotes whether server will run requests in serial (False) / parallel (True)!

        if self._threading:
            logging.info(self.prefix_message(u'Request threading Enabled!'))

        self.pool = ThreadPool(processes=threads if threads > 1 else 2)
        self.request_pool = ThreadPool(processes=request_threads)
        self.open_requests = []

        self.__stop = True

        self._server_socket = None

    def start(self):

        logging.info(self.prefix_message(u'Starting...'))

        self.__stop = False

        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind(self.server_address)
            self._server_socket.listen(5)

        except Exception as err:

            self._server_socket.close()

            logging.error(self.prefix_message(u'Failed to start.'))
            logging.exception(self.prefix_message(err))

            self.__stop = True

        if not self.__stop:
            logging.info(self.prefix_message(u'Started.'))

            # Run Main loop
            self.pool.apply_async(func=self.__main_loop)

    def stop(self):

        logging.info(self.prefix_message(u'Stopping. Waiting for processes to complete...'))

        # Signal loop termination
        self.__stop = True

        try:
            # Signal server termination
            self._server_socket.close()
            logging.debug(self.prefix_message(u'Shutting down...'))

        except Exception as err:
            logging.warning(self.prefix_message(u'Not started or failed to shut down properly.'))
            logging.warning(self.prefix_message(err))

        # Close the thread pool
        self.pool.close()
        self.request_pool.close()

        # Put the join in a separate thread so we can time it out if required!
        t_main = Thread(target=self.pool.join)
        t_main.start()

        t_req = Thread(target=self.request_pool.join)
        t_req.start()

        # Setup up a shutdown timeout so we can force exit if server does not gracefully close by itself!
        timer = Timeout(30)
        terminated = False

        # Wait for running processes to complete (pool.join is done)
        while t_main.is_alive() or t_req.is_alive():
            if timer.expired and not terminated:
                # Timer has expired so forcibly terminate the thread pool!
                logging.warning(self.prefix_message(u'Shutdown timer expired, terminating open requests...'))

                if t_main.is_alive():
                    self.pool.terminate()

                if t_req.is_alive():
                    self.request_pool.terminate()

                print(self.open_requests)

                # Force any open request sockets to shutdown.
                for r in self.open_requests:
                    r.shutdown()

                terminated = True

        logging.info(self.prefix_message(u'Stopped.'))

    def __main_loop(self):

        logging.debug(self.prefix_message(u'main loop ({t})'.format(t=currentThread().name)))

        # Run until stop requested!
        while not self.__stop:
            try:
                readable, _, _ = select([self._server_socket], [], [], 0)

                for sock in readable:
                    if sock is self._server_socket:
                        sock = self._server_socket.accept()

                        self.request_pool.apply_async(func=self.handle,
                                                      kwds=dict(source=sock[0]))

            except Exception as err:
                logging.error(self.prefix_message(err))
                logging.exception(err)

    @property
    def active(self):
        return not self.__stop

    def prefix_message(self,
                       msg):
        return u'MULTIPLEX Server on port {port}: {msg}'.format(port=self.multiplex_port,
                                                                msg=msg)

    def handle(self,
               source):
        MultiplexSocketHandler(source_socket=source,
                               server=self)


class MultiplexSocketHandler(object):

    def __init__(self,
                 source_socket,
                 server):

        # Save a reference to the server
        self.server = server

        # Register this request as an open request
        self.server.open_requests.append(self)

        self.source = source_socket
        self.destination = None

        # Forward the request to the correct server.
        self.forward(source=self.source)

    def prefix_message(self,
                       msg):
        return self.server.prefix_message(msg)

    def forward(self,
                source,
                destination=None):

        string = ' '

        while string:
            string = source.recv(1024)

            # first batch determines the destination
            if destination is None and string:
                destination = self.connect_destination(self.determine_protocol(string))

                self.server.request_pool.apply_async(func=self.forward,
                                                     kwds=dict(source=destination,
                                                               destination=source))

            # forwarding (started / running, finishing)
            if string:
                destination.sendall(string)

            else:
                self.shutdown(source=source,
                              destination=destination)

    def shutdown(self,
                 source=None,
                 destination=None):

        try:
            if source is None:
                self.source.shutdown(socket.SHUT_RDWR)

            else:
                source.shutdown(socket.SHUT_RD)

        except socket.error:
            pass

        try:
            if destination is None:
                self.destination.shutdown(socket.SHUT_RDWR)

            else:
                destination.shutdown(socket.SHUT_WR)

        except socket.error:
            pass

        if(source is None and destination is None) or source is self.destination:
            # UnRegister this request as an open request
            try:
                idx = self.server.open_requests.index(self)
                del self.server.open_requests[idx]

            except ValueError:
                pass

    def connect_destination(self,
                            http=True):
        logging.info(self.prefix_message(u'Creating destination socket to {proto} server on '
                                         u'port {port}.'.format(proto=u'HTTP' if http else u'HTTPS',
                                                                port=self.server.http_port if http
                                                                else self.server.https_port)))

        self.destination = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.destination.connect((self.server.destination_address[0],
                                  self.server.http_port
                                  if http else self.server.https_port))

        return self.destination

    @staticmethod
    def determine_protocol(string):

        for method in HTTP_METHODS:
            if string.startswith(method):
                return True

        return False


# run!
if __name__ == '__main__':

    svr = MultiplexServer(server_address=('', 443),
                          destination_address=('127.0.0.1', 8080),
                          destination_https_port=8443)

    try:
        svr.start()

        # wait for <ctrl-c>
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        svr.stop()

    except Exception:
        svr.stop()
