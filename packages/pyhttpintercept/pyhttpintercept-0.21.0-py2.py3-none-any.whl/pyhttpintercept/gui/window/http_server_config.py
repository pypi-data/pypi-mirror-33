# encoding: utf-8

from uiutil import RootWindow, ChildWindow
from ..frame.server_config import ServerConfigFrame


class _HTTPServerConfigWindow(object):

    def _draw_widgets(self):
        self.title(u'WebServer Config')
        self.dynamic_frame = ServerConfigFrame(parent=self._main_frame)


class HTTPServerConfigRootWindow(_HTTPServerConfigWindow, RootWindow):
    pass


class HTTPServerConfigChildWindow(_HTTPServerConfigWindow, ChildWindow):
    pass
