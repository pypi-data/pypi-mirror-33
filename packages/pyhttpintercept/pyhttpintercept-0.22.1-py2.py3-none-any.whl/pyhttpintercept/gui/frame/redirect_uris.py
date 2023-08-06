# encoding: utf-8

import logging_helper
from uiutil import BaseFrame
from uiutil.tk_names import HORIZONTAL, E, W, S, EW, NSEW, askquestion, StringVar, BooleanVar
from configurationutil import Configuration
from ...config import redirect
from ..window.redirect_uri import AddEditRedirectURIWindow

logging = logging_helper.setup_logging()


class RedirectURIConfigFrame(BaseFrame):

    def __init__(self,
                 address_list=None,
                 *args,
                 **kwargs):

        """

        :param address_list: (list)  List of domains to provide the user in the combobox.
                                     Each entry in the list can be either:
                                         --> (string) containing the domain name
                                         --> (tuple)  containing the domain name and a display name
                                                      e.g. ('google.co.uk', 'Google')
        :param args:
        :param kwargs:
        """

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._selected_record = StringVar(self.parent)

        self.cfg = Configuration()

        self._address_list = [] if address_list is None else address_list

        self.redirect_radio_list = {}
        self.redirect_active_var_list = {}
        self.redirect_active_list = {}

        self.columnconfigure(self.column.start(), weight=1)

        self.REDIRECT_ROW = self.row.next()
        self.rowconfigure(self.REDIRECT_ROW, weight=1)
        self.BUTTON_ROW = self.row.next()

        self._build_zone_frame()
        self._build_button_frame()

    def _build_zone_frame(self):

        self.record_frame = BaseFrame(self)
        self.record_frame.grid(row=self.REDIRECT_ROW,
                               column=self.column.current,
                               sticky=NSEW)

        self.record_frame.label(text=u'URI',
                                column=self.record_frame.column.start(),
                                sticky=W)
        self.rowconfigure(self.record_frame.column.current, weight=1)

        self.record_frame.label(text=u'Redirect URI',
                                column=self.record_frame.column.next(),
                                sticky=W)
        self.rowconfigure(self.record_frame.column.current, weight=1)

        self.record_frame.label(text=u'Status',
                                column=self.record_frame.column.next(),
                                sticky=W)

        self.record_frame.label(text=u'Active',
                                column=self.record_frame.column.next(),
                                sticky=W)

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=self.record_frame.column.start(),
                                    columnspan=4,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        for host, host_config in iter(redirect.get_redirection_config().items()):

            redirect_row = self.record_frame.row.next()

            if not self._selected_record.get():
                self._selected_record.set(host)

            uri_display_name = self._lookup_display_name(host)
            self.redirect_radio_list[host] = self.record_frame.radiobutton(text=uri_display_name
                                                                           if uri_display_name else host,
                                                                           variable=self._selected_record,
                                                                           value=host,
                                                                           row=redirect_row,
                                                                           column=self.record_frame.column.start(),
                                                                           sticky=W,
                                                                           tooltip=host
                                                                           if uri_display_name else u'')

            # Get the configured record
            redirect_uri = host_config[u'uri']
            redirect_uri_display_name = self._lookup_display_name(redirect_uri)
            self.record_frame.label(text=redirect_uri_display_name if redirect_uri_display_name else redirect_uri,
                                    row=redirect_row,
                                    column=self.record_frame.column.next(),
                                    sticky=W,
                                    tooltip=redirect_uri if redirect_uri_display_name else u'')

            self.record_frame.label(text=host_config[u'status'],
                                    row=redirect_row,
                                    column=self.record_frame.column.next(),
                                    sticky=W)

            self.redirect_active_var_list[host] = BooleanVar(self.parent)
            self.redirect_active_var_list[host].set(host_config[u'active'])

            self.redirect_active_list[host] = self.record_frame.checkbutton(
                variable=self.redirect_active_var_list[host],
                command=(lambda hst=host,
                         flag=self.redirect_active_var_list[host]:
                         self._update_active(host=hst,
                                             flag=flag)),
                row=redirect_row,
                column=self.record_frame.column.next(),
                sticky=W
            )

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=self.record_frame.column.start(),
                                    columnspan=4,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        self.record_frame.nice_grid()

    def _build_button_frame(self):

        button_width = 15

        self.button_frame = BaseFrame(self)
        self.button_frame.grid(row=self.BUTTON_ROW,
                               column=self.column.current,
                               sticky=(E, W, S))

        self.button(frame=self.button_frame,
                    name=u'_delete_record_button',
                    text=u'Delete Record',
                    width=button_width,
                    command=self._delete_uri_record,
                    row=self.button_frame.row.start(),
                    column=self.button_frame.column.start(),
                    tooltip=u'Delete\nselected\nrecord')

        self.button(frame=self.button_frame,
                    name=u'_add_record_button',
                    text=u'Add Record',
                    width=button_width,
                    command=self._add_uri_record,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next(),
                    tooltip=u'Add record\nto dns list')

        self.button(frame=self.button_frame,
                    name=u'_edit_record_button',
                    text=u'Edit Record',
                    width=button_width,
                    command=self._edit_uri_record,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next(),
                    tooltip=u'Edit\nselected\nrecord')

        self.button_frame.nice_grid()

    def _add_uri_record(self):
        window = AddEditRedirectURIWindow(fixed=True,
                                          parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()),
                                          address_list=self._address_list)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_zone_frame()

        self.parent.master.update_geometry()

    def _edit_uri_record(self):
        window = AddEditRedirectURIWindow(selected_record=self._selected_record.get(),
                                          edit=True,
                                          fixed=True,
                                          parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()),
                                          address_list=self._address_list)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_zone_frame()

        self.parent.master.update_geometry()

    def _delete_uri_record(self):
        result = askquestion(title=u"Delete Record",
                             message=u"Are you sure you "
                                     u"want to delete {r}?".format(r=self._selected_record.get()),
                             icon=u'warning',
                             parent=self)

        if result == u'yes':
            key = u'{c}.{h}'.format(c=redirect.REDIRECT_CFG,
                                    h=self._selected_record.get())

            del self.cfg[key]

            self.record_frame.destroy()
            self._build_zone_frame()

            self.parent.master.update_geometry()

    def _update_active(self,
                       host,
                       flag):
        key = u'{c}.{h}.{active}'.format(c=redirect.REDIRECT_CFG,
                                         h=host,
                                         active=redirect.ACTIVE)

        self.cfg[key] = flag.get()

    def _lookup_display_name(self,
                             address):

        display_name = u''

        # Check for a display name for host, accepting first match!
        for addr in self._address_list:
            if isinstance(addr, tuple):
                if address == addr[0] and addr[1]:
                    display_name = addr[1]
                    break  # We found our name so move on!

        return display_name
