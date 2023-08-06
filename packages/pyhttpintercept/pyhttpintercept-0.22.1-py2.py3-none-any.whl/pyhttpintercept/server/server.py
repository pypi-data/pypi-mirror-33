# encoding: utf-8

import os
import sys
import time
import logging_helper
from networkutil.addressing import get_my_addresses
from networkutil.ssl import generate_config_certificates, SSLConstant
from cryptography.x509 import SubjectAlternativeName, DNSName
from .._constants import SSL_CERT_SERVER
from ..exceptions import SSLError
from ..config import https_domains
from .webserver import WebServer
from .multiplexer import MultiplexServer
from .ssl_helper import check_ca_exists, get_ca

logging = logging_helper.setup_logging()

HTTP_MULTIPLEX_OFFSET = 10000
HTTPS_MULTIPLEX_OFFSET = 11000


class InterceptServer(object):

    DEFAULT_HTTP_PORTS = [80, ]
    DEFAULT_HTTPS_PORTS = [443, ]
    ALLOWED_HTTPS_DOMAINS = [address for address in get_my_addresses()]  # Local server addresses

    def __init__(self,
                 http_ports=None,
                 https_ports=None,
                 ssl_cert_path=None,
                 ssl_key_path=None):

        self._user_http_ports = self.DEFAULT_HTTP_PORTS if http_ports is None else http_ports
        self.http_ports = []
        self.http_server_instances = {}

        self._user_https_ports = self.DEFAULT_HTTPS_PORTS if https_ports is None else https_ports
        self.https_ports = []
        self.https_server_instances = {}

        self.multiplex_ports = []
        self.multiplex_server_instances = {}

        self.ssl_cert_path = ssl_cert_path
        self.ssl_key_path = ssl_key_path

        self._request_timeout = None

    def start(self,
              threaded=True):

        self.http_ports += self._user_http_ports
        self.https_ports += self._user_https_ports

        self.pre_start_tasks()

        # work out ports to multiplex
        self.multiplex_ports = list(set(self.http_ports) & set(self.https_ports))

        # Update multiplex server ports (+10000 http / +11000 https)
        for port in self.multiplex_ports:

            # Offset HTTP multiplexed port
            idx = self.http_ports.index(port)
            del self.http_ports[idx]
            self.http_ports.append(port + HTTP_MULTIPLEX_OFFSET)

            # Offset HTTPS multiplexed port
            idx = self.https_ports.index(port)
            del self.https_ports[idx]
            self.https_ports.append(port + HTTPS_MULTIPLEX_OFFSET)

        if (sys.platform == u'darwin'
                and os.geteuid() != 0
                and any(port <= 1024 for port in self.http_ports)
                and any(port <= 1024 for port in self.https_ports)
                and any(port <= 1024 for port in self.multiplex_ports)):
            raise Exception(u'You are running macOS please either restart with sudo or use ports > 1024!')

        logging.info(u'Starting up, use <Ctrl-C> to stop!')

        self._start_http(threaded=threaded)
        self._start_https(threaded=threaded)
        self._start_multiplexers(threaded=threaded)

        self.push_timeout_value_to_servers()

        self.post_start_tasks()

        logging.info(u'Ready...')

    def _start_http(self,
                    threaded=True):
        if self.http_ports:
            logging.info(u'Starting HTTP Servers.')

            # Start a HTTP server on each port in self.http_ports
            for http_port in self.http_ports:
                server_address = (u'', http_port)

                # Start HTTP Server
                self.http_server_instances[http_port] = WebServer(server_address=server_address,
                                                                  threading=threaded)

                self.http_server_instances[http_port].start()
                time.sleep(1)

    def _start_https(self,
                     threaded=True):
        if self.https_ports:
            logging.info(u'Starting HTTPS Servers.')

            # Generate the required server certificate unless provided
            if self.ssl_cert_path is None and self.ssl_key_path is None:
                self.generate_server_certificate()

            # Start a HTTPS server on each port in self.https_ports
            for https_port in self.https_ports:
                server_address = (u'', https_port)

                # Start HTTPS Server
                self.https_server_instances[https_port] = WebServer(server_address=server_address,
                                                                    threading=threaded,
                                                                    https=True,
                                                                    ssl_cert_path=self.ssl_cert_path,
                                                                    ssl_key_path=self.ssl_key_path)
                self.https_server_instances[https_port].start()
                time.sleep(1)

    def _start_multiplexers(self,
                            threaded=True):
        if self.multiplex_ports:
            logging.info(u'Starting MULTIPLEX Servers.')

            # Start a HTTP server on each port in self.http_ports
            for port in self.multiplex_ports:
                server_address = ('', port)
                dest_address = ('127.0.0.1', port + HTTP_MULTIPLEX_OFFSET)
                dest_https_port = port + HTTPS_MULTIPLEX_OFFSET

                # Start HTTP Server
                self.multiplex_server_instances[port] = MultiplexServer(server_address=server_address,
                                                                        destination_address=dest_address,
                                                                        destination_https_port=dest_https_port,
                                                                        threading=threaded)
                self.multiplex_server_instances[port].start()
                time.sleep(1)

    def stop(self):

        self.pre_stop_tasks()

        # Shutdown servers
        for multiplex_server in self.multiplex_server_instances.values():
            if multiplex_server.active:
                multiplex_server.stop()

        for http_server in self.http_server_instances.values():
            if http_server.active:
                http_server.stop()

        for https_server in self.https_server_instances.values():
            if https_server.active:
                https_server.stop()

        # Reset
        self.http_ports = []
        self.http_server_instances = {}

        self.https_ports = []
        self.https_server_instances = {}

        self.multiplex_ports = []
        self.multiplex_server_instances = {}

        self.post_stop_tasks()

        logging.info(u'Shut Down Complete')

    def reload_config(self):
        for http_server_instance in self.http_server_instances.values():
            http_server_instance.scenarios.reload_active_scenario()

        for https_server_instance in self.https_server_instances.values():
            https_server_instance.scenarios.reload_active_scenario()

    def pre_start_tasks(self):
        pass
        # override to performs tasks before the servers start

    def post_start_tasks(self):
        pass
        # override to performs tasks after the servers have started

    def pre_stop_tasks(self):
        pass
        # override to performs tasks before the servers start

    def post_stop_tasks(self):
        pass
        # override to performs tasks after the servers have started

    def generate_server_certificate(self):

        if not check_ca_exists():
            raise SSLError(u'Root CA must be generated before starting HTTPS servers!')

        dns_names = []

        for address in self.get_allowed_https_domains():
            try:
                dns_names.append(DNSName(address))

            except TypeError:
                pass

        extensions = [
            SubjectAlternativeName(dns_names)
        ]

        ca_cert, ca_key, ca_paths = get_ca()

        srv_cert, srv_key, srv_paths = generate_config_certificates(ca_cert=ca_cert,
                                                                    ca_key=ca_key,
                                                                    name=SSL_CERT_SERVER,
                                                                    extensions=extensions,
                                                                    passphrase=None,
                                                                    version1=True)

        self.ssl_cert_path = srv_paths.get(SSLConstant.pem)
        self.ssl_key_path = srv_paths.get(SSLConstant.private_key)

    def get_allowed_https_domains(self):

        cfg = https_domains.register_https_allowed_domain_cfg()

        key = u'{k}.{c}'.format(k=https_domains.HTTPS_DOMAIN_CFG,
                                c=https_domains.HTTPS_DOMAIN_LIST)
        domain_list = cfg[key]

        return list(set(self.ALLOWED_HTTPS_DOMAINS + domain_list))

    def push_timeout_value_to_servers(self):
        if self._request_timeout is not None:
            for server_instance in self.http_server_instances.values() + self.https_server_instances.values():
                server_instance.request_timeout = self._request_timeout

    @property
    def request_timeout(self):
        return self._request_timeout

    @request_timeout.setter
    def request_timeout(self,
                        value):
        self._request_timeout = value
        self.push_timeout_value_to_servers()
