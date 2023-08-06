# encoding: utf-8

from . import ParamsBaseConfigFrame
from uiutil import (Position,
                    Button)
from uiutil.tk_names import W


class ParamsListConfigFrame(ParamsBaseConfigFrame):

    HEADINGS = [
        u'Value'
    ]

    def __init__(self,
                 params=None,
                 *args,
                 **kwargs):

        self._params = [] if params is None else params

        if not isinstance(self._params, list):
            raise TypeError(u'Params are not of type list!')

        super(ParamsListConfigFrame, self).__init__(*args,
                                                    **kwargs)

    def _perform_delete(self,
                        selected):
        idx = self._params.index(selected)
        del self._params[idx]
        del self._param_elements[selected]

    def update_params(self):
        self._params = [self._param_elements[param].value
                        for param in self._param_elements
                        if self._param_elements[param].value]

    def _build_records_frame(self):
        super(ParamsListConfigFrame, self)._build_records_frame()
        self._scroll_frame.columnconfigure(0, weight=0)

    def _build_button_frame(self):

        super(ParamsListConfigFrame, self)._build_button_frame()

        Button(frame=self.button_frame,
               name=u'_move_up_button',
               text=u'▲',
               width=self.BUTTON_WIDTH,
               command=self._move_up,
               row=Position.CURRENT,
               column=Position.NEXT)

        Button(frame=self.button_frame,
               name=u'_move_down_button',
               text=u'▼',
               width=self.BUTTON_WIDTH,
               command=self._move_down,
               row=Position.CURRENT,
               column=Position.NEXT,
               sticky=W)

    def _move_up(self):
        selected = self.selected
        idx = self._params.index(selected)

        if idx > 0:
            self._move(idx,
                       idx - 1)

    def _move_down(self):
        selected = self.selected
        idx = self._params.index(selected)

        if idx < (len(self._params) - 1):
            self._move(idx,
                       idx + 1)

    def _move(self,
              idx,
              new_idx):
        temp = self._params[idx]
        self._params[idx] = self._params[new_idx]
        self._params[new_idx] = temp

        self._refresh_scroll_frame()

        self._radio_list[self._radio_list.keys()[0]].value = temp
