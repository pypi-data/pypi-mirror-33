# encoding: utf-8

from uiutil import RootWindow, ChildWindow
from ..frame.server_config import ServerConfigFrame


class _ServerConfigWindow(object):

    def _draw_widgets(self):
        self.title(u'WebServer Config')
        self.dynamic_frame = ServerConfigFrame(parent=self._main_frame)


class ServerConfigRootWindow(_ServerConfigWindow, RootWindow):
    pass


class ServerConfigChildWindow(_ServerConfigWindow, ChildWindow):
    pass
