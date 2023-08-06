# encoding: utf-8

import logging_helper
from uiutil.tk_names import W, E, EW, NORMAL, DISABLED
from uiutil import BaseFrame, Button, Position, Switch, Label, Spinbox
from ..._constants import THREADED
from ...config.persistent_fields import server_threading, request_timeout
from ..window.scenarios import ScenariosConfigWindow
from ..window.scenario import AddEditScenarioWindow
from ..window.redirect_uris import RedirectURIConfigWindow

logging = logging_helper.setup_logging()


class HTTPServerConfigFrame(BaseFrame):

    BUTTON_WIDTH = 15

    def __init__(self,
                 intercept_server=None,
                 redirect_address_list=None,
                 *args,
                 **kwargs):

        self.intercept_server = intercept_server
        self.redirect_address_list = redirect_address_list

        super(HTTPServerConfigFrame, self).__init__(*args,
                                                    **kwargs)

        Button(text=u'Redirect URIs',
               width=self.BUTTON_WIDTH,
               sticky=EW,
               command=self.launch_redirection_config,
               tooltip=u'Configure the URIs\n'
                       u'you want to redirect')

        # TODO: we should be able to configure without requiring a server instance!
        Button(text=u'Scenarios',
               width=self.BUTTON_WIDTH,
               sticky=EW,
               column=Position.NEXT,
               command=self.launch_scenarios_config,
               state=DISABLED if self.intercept_server is None else NORMAL,
               tooltip=u'Modify, add\n'
                       u'or remove\n'
                       u'scenarios')

        Button(text=u'Active Scenario',
               width=self.BUTTON_WIDTH,
               sticky=EW,
               column=Position.NEXT,
               command=self.launch_active_scenario_config,
               state=DISABLED if self.intercept_server is None else NORMAL,
               tooltip=u'Configure settings\n'
                       u'for the current\n'
                       u'active scenario')

        subframe = BaseFrame(column=Position.NEXT,
                             sticky=EW)

        Label(frame=subframe,
              text=u'Request Timeout:',
              sticky=EW,
              tooltip=u'Modify to alter the timeout\n'
                      u'for making actual requests.')

        Spinbox(frame=subframe,
                link=request_timeout,
                values=(0.1, 0.5, 1, 1.5, 2, 3, 5, 10, 30, 60),
                width=3,
                column=Position.NEXT,
                sticky=EW)

        request_timeout.register_observer(self)

        self.threaded_switch = Switch(frame=subframe,
                                      text=THREADED,
                                      switch_state=Switch.ON,
                                      link=server_threading,
                                      row=Position.NEXT,
                                      column=Position.START,
                                      columnspan=2,
                                      sticky=EW,
                                      tooltip=u"Check to Run intercept\n"
                                              u"with threading enabled")

        self.nice_grid()

    def notification(self,
                     notifier,
                     **kwargs):
        if notifier == request_timeout:
            self.intercept_server.request_timeout = float(request_timeout.value)

    def launch_redirection_config(self):
        RedirectURIConfigWindow(fixed=True,
                                parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()),
                                address_list=self.redirect_address_list)

    def launch_scenarios_config(self):
        window = ScenariosConfigWindow(fixed=True,
                                       intercept_server=self.intercept_server,
                                       parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        try:
            self.intercept_server.reload_config()
        except AttributeError as e:
            logging.exception(e)

    def launch_active_scenario_config(self):

        window = AddEditScenarioWindow(edit=True,
                                       fixed=True,
                                       intercept_server=self.intercept_server,
                                       parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        try:
            self.intercept_server.reload_config()
        except AttributeError as e:
            logging.exception(e)
