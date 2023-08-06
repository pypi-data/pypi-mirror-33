# encoding: utf-8

from uiutil import RootWindow, ChildWindow
from ..frame.ssl_config import SSLConfigFrame


class _SSLConfigWindow(object):

    def _draw_widgets(self):
        self.title(u'SSL Config')
        self.dynamic_frame = SSLConfigFrame(parent=self._main_frame)


class SSLConfigRootWindow(_SSLConfigWindow, RootWindow):
    pass


class SSLConfigChildWindow(_SSLConfigWindow, ChildWindow):
    pass
