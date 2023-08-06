# encoding: utf-8

from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass
from collections import OrderedDict
from uiutil import (BaseScrollFrame,
                    BaseFrame,
                    Position,
                    Separator,
                    Label,
                    Button,
                    TextEntry,
                    RadioButton)
from uiutil.tk_names import (askquestion,
                             E,
                             W,
                             S,
                             NSEW,
                             EW)


class ParamsBaseConfigFrame(with_metaclass(ABCMeta, BaseFrame, object)):

    BUTTON_WIDTH = 2
    KEY_ENTRY_WIDTH = 15
    VALUE_ENTRY_WIDTH = 30
    HEADINGS = [
        u'Key',
        u'Value'
    ]

    def __init__(self,
                 sort_params=False,
                 canvas_height=120,
                 canvas_width=460,
                 *args,
                 **kwargs):

        super(ParamsBaseConfigFrame, self).__init__(*args,
                                                    **kwargs)

        self._sort_params = sort_params
        self._canvas_height = canvas_height
        self._canvas_width = canvas_width

        self._radio_list = OrderedDict()
        self._param_elements = OrderedDict()

        self._draw()

    def _draw(self):

        self._build_headings_frame()

        Separator(row=Position.NEXT,
                  column=Position.START)

        self._build_records_frame()

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

        Separator(frame=self.headings_frame,
                  row=Position.NEXT,
                  column=Position.START,
                  columnspan=len(self.HEADINGS))

        self.headings_frame.nice_grid_columns()

    def _build_records_frame(self):

        self._scroll_frame = BaseScrollFrame(parent=self,
                                             canvas_height=self._canvas_height,
                                             canvas_width=self._canvas_width)
        self._scroll_frame.grid(row=1,
                                column=0,
                                sticky=NSEW)

        self.draw_records()

        self._scroll_frame.nice_grid_columns()

    def draw_records(self):

        select_next_row = True

        params = sorted(self._params) if self._sort_params else self._params

        for param in params:
            self._draw_param(param)

            if select_next_row:
                self._radio_list[param].value = param
                select_next_row = False

        self._draw_param(u'')

    def _draw_param(self,
                    key):

        self._radio_list[key] = RadioButton(frame=self._scroll_frame,
                                            value=key,
                                            row=Position.NEXT,
                                            column=Position.START,
                                            sticky=W)

        key_entry = TextEntry(frame=self._scroll_frame,
                              value=key,
                              width=self.KEY_ENTRY_WIDTH,
                              row=Position.CURRENT,
                              column=Position.NEXT,
                              sticky=EW)

        self._param_elements[key] = key_entry

    def _build_button_frame(self):

        self.button_frame = BaseFrame(row=Position.NEXT,
                                      column=Position.START,
                                      sticky=(E, S))

        Button(frame=self.button_frame,
               name=u'_delete_record_button',
               text=u'-',
               width=self.BUTTON_WIDTH,
               command=self._delete,
               row=Position.START,
               column=Position.START)

        Button(frame=self.button_frame,
               name=u'_add_record_button',
               text=u'+',
               width=self.BUTTON_WIDTH,
               command=self._add,
               row=Position.CURRENT,
               column=Position.NEXT)

        self.button_frame.nice_grid()

    def _add(self):
        self.update_params()
        self._refresh_scroll_frame()

    def _delete(self):
        selected = self._radio_list[self._radio_list.keys()[0]].value

        if selected:
            result = askquestion(u"Delete Record",
                                 u"Are you sure you want to delete {r}?".format(r=selected),
                                 icon=u'warning',
                                 parent=self)

            if result == u'yes':
                self._perform_delete(selected=selected)

                self.update_params()
                self._refresh_scroll_frame()

    def _refresh_scroll_frame(self):

        self._radio_list = OrderedDict()
        self._param_elements = OrderedDict()

        self._scroll_frame.destroy()
        self._build_records_frame()
        self.nice_grid()

        self.update_geometry()

    @abstractmethod
    def _perform_delete(self,
                        selected):
        pass

    @abstractmethod
    def update_params(self):
        pass

    @property
    def params(self):
        return self._params
