# encoding: utf-8

import logging_helper
from uiutil import BaseFrame, Label, Button, TextEntry, Separator, Position
from uiutil.tk_names import E, EW, showerror
from ...config import https_domains


logging = logging_helper.setup_logging()


class AddEditHTTPSDomainFrame(BaseFrame):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self.edit = edit

        self.cfg = https_domains.register_https_allowed_domain_cfg()

        self.cfg_key = u'{k}.{c}'.format(k=https_domains.HTTPS_DOMAIN_CFG,
                                         c=https_domains.HTTPS_DOMAIN_LIST)

        self.domain_list = self.cfg[self.cfg_key]

        try:
            self.selected_idx = self.domain_list.index(selected_record)

        except ValueError:
            self.selected_idx = -1

        if self.selected_idx > -1:
            self.selected_domain = self.domain_list[self.selected_idx]

        else:
            self.selected_domain = u''

        self._draw()

    def _draw(self):

        Label(text=u'Domain:',
              row=Position.START,
              column=Position.START,
              sticky=E)

        self._domain = TextEntry(value=self.selected_domain,
                                 row=Position.CURRENT,
                                 column=Position.NEXT,
                                 sticky=EW,
                                 columnspan=3)

        self.columnconfigure(self.column.current, weight=1)

        Separator(row=Position.NEXT,
                  column=Position.START,
                  columnspan=4)

        Button(text=u'Cancel',
               width=15,
               command=self._cancel,
               row=Position.NEXT,
               column=Position.NEXT)

        Button(text=u'Save',
               width=15,
               command=self._save,
               row=Position.CURRENT,
               column=Position.NEXT)

    def _save(self):

        domain = self._domain.value.strip()

        try:
            if self.edit:
                # Remove the original value before inserting the replacement
                del self.domain_list[self.selected_idx]

                self.domain_list.insert(self.selected_idx, domain)

            else:
                self.domain_list.append(domain)

            self.cfg[self.cfg_key] = sorted(self.domain_list)

            self.parent.master.exit()

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.exception(err)
            showerror(title=u'Save Failed',
                      message=u'Cannot Save Record: {err}'.format(err=err))

    def _cancel(self):
        self.parent.master.exit()
