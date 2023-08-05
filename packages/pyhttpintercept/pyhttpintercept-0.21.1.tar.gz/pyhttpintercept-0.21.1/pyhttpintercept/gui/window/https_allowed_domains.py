# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.https_allowed_domains import HTTPSAllowedDomainsConfigFrame

logging = logging_helper.setup_logging()


class HTTPSAllowedDomainsConfigWindow(ChildWindow):

    def _draw_widgets(self):
        self.title(u"HTTPS Allowed Domains")

        self.config = HTTPSAllowedDomainsConfigFrame(parent=self._main_frame,
                                                     sticky=NSEW)
