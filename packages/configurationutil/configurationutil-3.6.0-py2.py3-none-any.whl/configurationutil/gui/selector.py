# encoding: utf-8

import logging_helper
from future.utils import with_metaclass
from abc import abstractmethod, ABCMeta
from uiutil import BaseScrollFrame, BaseFrame, Position, Separator, Label, Button, RadioButton
from uiutil.tk_names import askquestion, E, W, S, NSEW
from ..configuration import Configuration

logging = logging_helper.setup_logging()


class ConfigSelectorFrame(with_metaclass(ABCMeta, BaseFrame)):

    SCROLL_HEIGHT = 120
    SCROLL_WIDTH = 220
    BUTTON_WIDTH = 15

    HEADINGS = []

    ADD_EDIT_WINDOW_CLASS = None

    CONFIG_ROOT = None

    def __init__(self,
                 items,
                 cfg=Configuration,
                 *args,
                 **kwargs):

        """

        :param items:   Should be a CfgItems object
        :param cfg:     Configuration object
        :param args:
        :param kwargs:
        """

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._cfg = cfg()
        self._items = items()
        self._add_edit_kwargs = {}

        self._radio_list = {}
        self._item_zero = None

        self._build_headings_frame()

        Separator(row=Position.NEXT,
                  column=Position.START)

        self._scroll_wrapper_frame = BaseFrame(parent=self,
                                               row=Position.NEXT,
                                               column=Position.START,
                                               sticky=NSEW)

        self._build_records_frame()

        self._scroll_wrapper_frame.nice_grid()

        Separator(row=Position.NEXT,
                  column=Position.START)

        self._build_button_frame()

        self.nice_grid()

    def _build_headings_frame(self):

        self.headings_frame = BaseFrame(row=Position.START,
                                        column=Position.START,
                                        sticky=NSEW)

        for heading in self.HEADINGS:
            Label(frame=self.headings_frame,
                  text=heading,
                  column=Position.START if heading == self.HEADINGS[0] else Position.NEXT,
                  row=Position.CURRENT,
                  sticky=W)

        # TODO: Fix heading placement to match up with columns!
        self.headings_frame.nice_grid_columns()

    def _build_records_frame(self):

        self._scroll_frame = BaseScrollFrame(parent=self._scroll_wrapper_frame,
                                             canvas_height=self.SCROLL_HEIGHT,
                                             canvas_width=self.SCROLL_WIDTH,
                                             row=Position.START,
                                             column=Position.START,
                                             sticky=NSEW)

        self.draw_records()

        self._scroll_frame.nice_grid_columns()

    def draw_records(self):

        """ Draw the config records. """

        select_next_row = True

        self._items.reset_cache()

        sorted_items = sorted(self._items)

        # Get first item for use as primary radio button
        self._item_zero = sorted_items[0] if sorted_items else None

        for item in sorted_items:
            self._radio_list[item] = RadioButton(frame=self._scroll_frame,
                                                 text=item,
                                                 associate=True
                                                 if item == self._item_zero
                                                 else self._radio_list[self._item_zero],
                                                 row=Position.NEXT,
                                                 column=Position.START,
                                                 sticky=W)

            if select_next_row:
                self._radio_list[self._item_zero].value = item
                select_next_row = False

            self.draw_additional_columns(item=item)

    @abstractmethod
    def draw_additional_columns(self,
                                item):

        """ Draw additional info fields for each record.

        Please use self._scroll_frame as the parent frame for UI elements.

        """

        pass

    def _build_button_frame(self):

        self.button_frame = BaseFrame(row=Position.NEXT,
                                      column=Position.START,
                                      sticky=(E, W, S))

        Button(frame=self.button_frame,
               name=u'_delete_record_button',
               text=u'Delete',
               width=self.BUTTON_WIDTH,
               command=self._delete,
               row=Position.START,
               column=Position.START)

        Button(frame=self.button_frame,
               name=u'_add_record_button',
               text=u'Add',
               width=self.BUTTON_WIDTH,
               command=self._add,
               row=Position.CURRENT,
               column=Position.NEXT)

        Button(frame=self.button_frame,
               name=u'_edit_record_button',
               text=u'Edit',
               width=self.BUTTON_WIDTH,
               command=self._edit,
               row=Position.CURRENT,
               column=Position.NEXT)

        self.button_frame.nice_grid()

    def _add(self):
        window = self.ADD_EDIT_WINDOW_CLASS(fixed=True,
                                            parent_geometry=self.parent.winfo_toplevel().winfo_geometry(),
                                            **self._add_edit_kwargs)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self._scroll_frame.destroy()
        self._build_records_frame()
        self._scroll_wrapper_frame.nice_grid()
        self.nice_grid()

        self.parent.master.update_geometry()

    def _edit(self):
        window = self.ADD_EDIT_WINDOW_CLASS(selected_record=self._radio_list[self._item_zero].value,
                                            edit=True,
                                            fixed=True,
                                            parent_geometry=self.parent.winfo_toplevel().winfo_geometry(),
                                            **self._add_edit_kwargs)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self._scroll_frame.destroy()
        self._build_records_frame()
        self._scroll_wrapper_frame.nice_grid()
        self.nice_grid()

        self.parent.master.update_geometry()

    def _delete(self):
        selected = self._radio_list[self._item_zero].value

        result = askquestion(u"Delete Record",
                             u"Are you sure you want to delete {r}?".format(r=selected),
                             icon=u'warning',
                             parent=self)

        if result == u'yes':
            key = u'{cfg}.{int}'.format(cfg=self.CONFIG_ROOT,
                                        int=selected)

            del self._cfg[key]

            self._scroll_frame.destroy()
            self._build_records_frame()
            self._scroll_wrapper_frame.nice_grid()
            self.nice_grid()

            self.parent.master.update_geometry()
