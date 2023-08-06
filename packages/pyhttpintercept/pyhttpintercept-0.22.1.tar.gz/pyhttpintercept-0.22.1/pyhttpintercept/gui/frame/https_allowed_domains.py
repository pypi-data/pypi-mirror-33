# encoding: utf-8

import logging_helper
from uiutil import BaseFrame, Position, Button, Separator
from uiutil.tk_names import HORIZONTAL, E, W, S, EW, NSEW, askquestion, StringVar
from ...config import https_domains
from ..window.https_domain import AddEditHTTPSDomainWindow

logging = logging_helper.setup_logging()


class HTTPSAllowedDomainsConfigFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._selected_record = StringVar(self.parent)

        self.cfg = https_domains.register_https_allowed_domain_cfg()

        self.redirect_radio_list = {}

        self.columnconfigure(self.column.start(), weight=1)

        self.REDIRECT_ROW = self.row.next()
        self.rowconfigure(self.REDIRECT_ROW, weight=1)
        self.BUTTON_ROW = self.row.next()

        self._build_https_domain_frame()
        self._build_button_frame()

    def _build_https_domain_frame(self):

        self.record_frame = BaseFrame(self,
                                      row=Position.START,
                                      column=Position.START,
                                      sticky=NSEW)

        self.record_frame.label(text=u'Domain',
                                column=self.record_frame.column.start(),
                                sticky=W)
        self.rowconfigure(self.record_frame.column.current, weight=1)

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=self.record_frame.column.start(),
                                    columnspan=4,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        key = u'{k}.{c}'.format(k=https_domains.HTTPS_DOMAIN_CFG,
                                c=https_domains.HTTPS_DOMAIN_LIST)
        domain_list = self.cfg[key]

        for domain in sorted(domain_list):

            redirect_row = self.record_frame.row.next()

            if not self._selected_record.get():
                self._selected_record.set(domain)

            self.redirect_radio_list[domain] = self.record_frame.radiobutton(text=domain,
                                                                             variable=self._selected_record,
                                                                             value=domain,
                                                                             row=redirect_row,
                                                                             column=self.record_frame.column.start(),
                                                                             sticky=W)

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

        self.button_frame = BaseFrame(self,
                                      row=Position.NEXT,
                                      column=Position.START,
                                      sticky=(E, W, S))

        Button(frame=self.button_frame,
               name=u'_add_record_button',
               text=u'Add Record',
               width=button_width,
               command=self._add_uri_record,
               row=Position.START,
               column=Position.START)

        Button(frame=self.button_frame,
               name=u'_edit_record_button',
               text=u'Edit Record',
               width=button_width,
               command=self._edit_uri_record,
               row=Position.NEXT,
               column=Position.START)

        Button(frame=self.button_frame,
               name=u'_delete_record_button',
               text=u'Delete Record',
               width=button_width,
               command=self._delete_uri_record,
               row=Position.NEXT,
               column=Position.START)

        self.button_frame.nice_grid()

    def _add_uri_record(self):
        window = AddEditHTTPSDomainWindow(fixed=True,
                                          parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_https_domain_frame()

        self.parent.master.update_geometry()

    def _edit_uri_record(self):
        window = AddEditHTTPSDomainWindow(selected_record=self._selected_record.get(),
                                          edit=True,
                                          fixed=True,
                                          parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_https_domain_frame()

        self.parent.master.update_geometry()

    def _delete_uri_record(self):
        result = askquestion(title=u"Delete Record",
                             message=u"Are you sure you "
                                     u"want to delete {r}?".format(r=self._selected_record.get()),
                             icon=u'warning',
                             parent=self)

        if result == u'yes':
            key = u'{k}.{c}'.format(k=https_domains.HTTPS_DOMAIN_CFG,
                                    c=https_domains.HTTPS_DOMAIN_LIST)
            domain_list = self.cfg[key]

            idx = domain_list.index(self._selected_record.get())

            del domain_list[idx]

            self.cfg[key] = sorted(domain_list)

            self.record_frame.destroy()
            self._build_https_domain_frame()

            self.parent.master.update_geometry()
