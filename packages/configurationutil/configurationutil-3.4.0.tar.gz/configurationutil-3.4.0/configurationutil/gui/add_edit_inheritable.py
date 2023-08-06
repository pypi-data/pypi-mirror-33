# encoding: utf-8

import logging_helper
from future.utils import with_metaclass
from abc import abstractmethod, ABCMeta
from configurationutil import DefaultInheritableConstant, Configuration
from uiutil import BaseFrame, Button, Position, Separator, Label, Combobox, TextEntry, Switch
from uiutil.tk_names import E, W, S, EW, showerror

logging = logging_helper.setup_logging()


class AddEditInheritableConfigFrame(with_metaclass(ABCMeta, BaseFrame)):

    BUTTON_WIDTH = 12

    CONFIG_ROOT = None
    DEFAULTS_KEY = DefaultInheritableConstant.defaults

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 cfg=Configuration,
                 inheritable_items=None,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.edit = edit

        self._cfg = cfg()
        self._inheritable_items = [] if inheritable_items is None else inheritable_items

        if selected_record:
            key = u'{cfg}.{int}'.format(cfg=self.CONFIG_ROOT,
                                        int=selected_record)
            self._selected_record_name = selected_record
            self.selected_record = self._cfg[key]

        else:
            self._selected_record_name = u''
            self.selected_record = None

        self._draw()

        Separator(row=Position.NEXT,
                  column=Position.START,
                  columnspan=2)

        self._build_button_frame()

        self.nice_grid()

    @property
    def selected_record_name(self):
        return self._selected_record_name if self.edit else self._name.value

    def _draw(self):

        if self.edit:
            Label(text=self._selected_record_name,
                  font=u'-size 18',
                  row=Position.START,
                  column=Position.START,
                  sticky=EW)

        else:
            Label(text=u'Name:',
                  row=Position.START,
                  column=Position.START,
                  sticky=E)

            self._name = TextEntry(value=u'',
                                   row=Position.CURRENT,
                                   column=Position.NEXT,
                                   sticky=EW)

        if self._selected_record_name:
            idx = self._inheritable_items.index(self._selected_record_name)
            if idx > -1:
                del self._inheritable_items[idx]

        Separator(row=Position.NEXT,
                  column=Position.START,
                  columnspan=2)

        Label(text=u'Inherits:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._inherits = Combobox(value=self.selected_record.get(DefaultInheritableConstant.inherits, u'')
                                  if self.edit else u'',
                                  values=[u''] + self._inheritable_items,
                                  row=Position.CURRENT,
                                  column=Position.NEXT,
                                  sticky=EW)

        Label(text=u'Hidden:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._hidden = Switch(switch_state=self.selected_record.get(DefaultInheritableConstant.hidden, Switch.OFF)
                              if self.edit else Switch.OFF,
                              row=Position.CURRENT,
                              column=Position.NEXT,
                              sticky=W)

        Separator(row=Position.NEXT,
                  column=Position.START,
                  columnspan=2)

        self.draw_defaults()

    @property
    def defaults(self):
        return self.selected_record.get(self.DEFAULTS_KEY, {}) if self.edit else {}

    @abstractmethod
    def draw_defaults(self):

        """ Draw the defaults entry fields. """

        pass

    def _build_button_frame(self):

        self.button_frame = BaseFrame(row=Position.NEXT,
                                      column=Position.START,
                                      sticky=(E, W, S),
                                      columnspan=2)

        Button(frame=self.button_frame,
               text=u'Cancel',
               width=self.BUTTON_WIDTH,
               command=self._cancel,
               row=Position.NEXT,
               column=Position.START,
               sticky=EW)

        Button(frame=self.button_frame,
               text=u'Save',
               width=self.BUTTON_WIDTH,
               command=self._save,
               row=Position.CURRENT,
               column=Position.NEXT,
               sticky=EW)

        self.button_frame.nice_grid()

    def save_other(self,
                   new_host):

        """ prepare any other params for saving. """

        return new_host

    @abstractmethod
    def save_defaults(self):

        """ prepare the defaults dict for saving. """

        pass

    def _save(self):

        try:
            if not self.selected_record_name:
                raise ValueError(u'Name cannot be blank!')

            new_record = {
                self.DEFAULTS_KEY: self.save_defaults()
            }

            if self._inherits.value:
                new_record[DefaultInheritableConstant.inherits] = self._inherits.value

            if self._hidden.value:
                new_record[DefaultInheritableConstant.hidden] = self._hidden.value

            new_record = self.save_other(new_record)

            key = u'{cfg}.{ep}'.format(cfg=self.CONFIG_ROOT,
                                       ep=self.selected_record_name)

            self._cfg[key] = new_record

            self.parent.master.exit()

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.exception(err)
            showerror(title=u'Save Failed',
                      message=u'Cannot Save: {err}'.format(err=err))

    def _cancel(self):
        self.parent.master.exit()
