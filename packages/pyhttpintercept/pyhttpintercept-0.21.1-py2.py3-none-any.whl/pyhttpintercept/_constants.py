# encoding: utf-8

from ._metadata import __module_name__

PROFILER_PROFILE_ID = __module_name__

THREADED = u'Threaded'
SERVER_THREADING_KEY = u'PyHTTPIntercept/Threading'

SERVER_REQUEST_TIMEOUT = u'PyHTTPIntercept/Request Timeout'
DEFAULT_SERVER_REQUEST_TIMEOUT = 1.5

START_SERVERS = u'Start WebServers'
STOP_SERVERS = u'Stop WebServers'

SSL_CERT_CA = u'PyHTTPInterceptCA'
SSL_CERT_SERVER = u'PyHTTPInterceptSERVER'
SSL_PROFILE_NAME = u'PyHTTPIntercept'
