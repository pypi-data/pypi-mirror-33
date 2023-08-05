# encoding: utf-8

import logging_helper
from uiutil.tk_names import NORMAL, DISABLED, EW, showerror
from uiutil import Position, BaseFrame, Button, Separator
from ..._constants import START_SERVERS, STOP_SERVERS
from ...config.persistent_fields import server_threading
from ...server import InterceptServer
from ..frame.server_config import ServerConfigFrame

logging = logging_helper.setup_logging()


class ServerFrame(BaseFrame):

    BUTTON_WIDTH = 20

    def __init__(self,
                 server=InterceptServer,
                 server_kwargs=None,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        if server_kwargs is None:
            server_kwargs = {}

        self.intercept_server = server(**server_kwargs)

        self.intercept_config = ServerConfigFrame(intercept_server=self.intercept_server,
                                                  sticky=EW)

        Separator(row=Position.NEXT)

        self.start_stop_button = Button(state=NORMAL,
                                        value=START_SERVERS,
                                        width=self.BUTTON_WIDTH,
                                        command=self.start_stop,
                                        column=Position.START,
                                        row=Position.NEXT,
                                        sticky=EW,
                                        tooltip=u'')

        self.columnconfigure(1, weight=1)

    def start_stop(self):
        if self.start_stop_button.value == START_SERVERS:
            self.start()
        else:
            self.stop()

    def start(self):

        try:
            self.intercept_server.start(threaded=server_threading.get())
            self.start_stop_button.value = STOP_SERVERS
            self.intercept_config.http.threaded_switch.disable()
            self.intercept_config.ssl.https_domains_button.config(state=DISABLED)

        except Exception as err:
            logging.exception(err)
            logging.fatal(u'Unexpected Exception.')

            showerror(title=u'WebServer startup failed!',
                      message=u'Failed to start intercept webservers: {err}'.format(err=err))

            self.stop()

    def stop(self):

        self.intercept_server.stop()
        self.start_stop_button.value = START_SERVERS
        self.intercept_config.http.threaded_switch.enable()
        self.intercept_config.ssl.https_domains_button.config(state=NORMAL)
        self.start_stop_button.tooltip.text = (u'Start Intercept\n'
                                               u'WebServers for\n'
                                               u'active devices')
