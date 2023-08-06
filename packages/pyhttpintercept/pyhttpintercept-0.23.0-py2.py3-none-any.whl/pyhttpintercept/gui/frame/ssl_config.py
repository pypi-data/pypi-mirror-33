# encoding: utf-8

import logging_helper
from uiutil.tk_names import EW, NORMAL, DISABLED, asksaveasfilename
from uiutil import BaseFrame, Button, Position
from ..window.https_allowed_domains import HTTPSAllowedDomainsConfigWindow
from ..._constants import SSL_PROFILE_NAME
from ...server.ssl_helper import (create_ca,
                                  check_ca_exists,
                                  create_apple_configurator_profile)


logging = logging_helper.setup_logging()


class SSLConfigFrame(BaseFrame):

    BUTTON_WIDTH = 15

    def __init__(self,
                 *args,
                 **kwargs):

        super(SSLConfigFrame, self).__init__(*args,
                                             **kwargs)

        self._generate_ca_button = Button(text=u'Generate Root CA',
                                          width=self.BUTTON_WIDTH,
                                          sticky=EW,
                                          command=self.generate_ca,
                                          state=DISABLED if check_ca_exists() else NORMAL,
                                          tooltip=u'Generates a Root CA for this server.\n'
                                                  u'If this is not done you will be unable\n'
                                                  u'to start HTTPS Servers!')

        self._save_profile_button = Button(text=u'Save Profile',
                                           width=self.BUTTON_WIDTH,
                                           sticky=EW,
                                           column=Position.NEXT,
                                           command=self.save_profile,
                                           state=NORMAL if check_ca_exists() else DISABLED,
                                           tooltip=u'Create and save a configurator profile\n'
                                                   u'for adding to an Apple device that will\n'
                                                   u'allow it to trust certificates signed by\n'
                                                   u'our Root CA.')

        self.https_domains_button = Button(text=u'HTTPS Domains',
                                           width=self.BUTTON_WIDTH,
                                           sticky=EW,
                                           column=Position.NEXT,
                                           command=self.launch_https_domains_config,
                                           tooltip=u'Configure domains that will\n'
                                                   u'be added to the HTTPS server\n'
                                                   u'certificate.  Any domains not\n'
                                                   u'listed will not be able to\n'
                                                   u'be trusted by clients!')

        self.nice_grid()

    def generate_ca(self):
        create_ca()

        if check_ca_exists():
            self._generate_ca_button.config(state=DISABLED)
            self._save_profile_button.config(state=NORMAL)

    def save_profile(self):

        # Ask the user where to save the profile
        out_file = asksaveasfilename(parent=self,
                                     initialdir=u'~/',
                                     initialfile=SSL_PROFILE_NAME,
                                     defaultextension=u'.mobileconfig',
                                     title=u'Save Profile')

        if out_file:
            # Save the profile
            create_apple_configurator_profile(out_file)

    def launch_https_domains_config(self):

        window = HTTPSAllowedDomainsConfigWindow(edit=True,
                                                 fixed=True,
                                                 parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)
