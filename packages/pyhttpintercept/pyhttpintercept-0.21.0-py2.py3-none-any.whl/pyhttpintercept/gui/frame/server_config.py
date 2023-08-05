# encoding: utf-8

import logging_helper
from uiutil.tk_names import EW
from uiutil import BaseLabelFrame, Position
from .http_server_config import HTTPServerConfigFrame
from .ssl_config import SSLConfigFrame

logging = logging_helper.setup_logging()


class ServerConfigFrame(BaseLabelFrame):

    BUTTON_WIDTH = 15

    def __init__(self,
                 title=u'WebServer Config:',
                 intercept_server=None,
                 redirect_address_list=None,
                 *args,
                 **kwargs):

        super(ServerConfigFrame, self).__init__(title=title,
                                                *args,
                                                **kwargs)

        self.http = HTTPServerConfigFrame(intercept_server=intercept_server,
                                          redirect_address_list=redirect_address_list,
                                          column=Position.START,
                                          row=Position.START,
                                          sticky=EW)

        self.ssl = SSLConfigFrame(column=Position.START,
                                  row=Position.NEXT,
                                  sticky=EW)

        self.nice_grid()
