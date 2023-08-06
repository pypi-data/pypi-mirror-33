# encoding: utf-8

import logging_helper
from uiutil.tk_names import EW
from uiutil import RootWindow, ChildWindow
from ...server.server import InterceptServer
from ..frame.server import ServerFrame

logging = logging_helper.setup_logging()


class _ServerWindow(object):

    def __init__(self,
                 server=InterceptServer,
                 server_kwargs=None,
                 *args,
                 **kwargs):

        self.server = server
        self.server_kwargs = server_kwargs

        super(_ServerWindow, self).__init__(*args,
                                            **kwargs)

    def _draw_widgets(self):
        self.title(u"WebServer (Redirect, Host, Intercept & Proxy)")

        self.intercept = ServerFrame(server=self.server,
                                     server_kwargs=self.server_kwargs,
                                     sticky=EW)

    def close(self):
        self.intercept.intercept_server.stop()


class ServerRootWindow(_ServerWindow, RootWindow):

    DEBUG_MENU_ENABLED = True

    def __init__(self,
                 *args,
                 **kwargs):
        super(ServerRootWindow, self).__init__(fixed=True,
                                               *args,
                                               **kwargs)


class ServerChildWindow(_ServerWindow, ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):
        super(ServerChildWindow, self).__init__(fixed=True,
                                                *args,
                                                **kwargs)
