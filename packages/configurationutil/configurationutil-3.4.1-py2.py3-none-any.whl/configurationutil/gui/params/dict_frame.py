# encoding: utf-8

from collections import Mapping
from uiutil import Position, TextEntry
from uiutil.tk_names import EW
from . import ParamsBaseConfigFrame


class ParamsDictConfigFrame(ParamsBaseConfigFrame):

    HEADINGS = [
        u'Key',
        u'Value'
    ]

    def __init__(self,
                 params=None,
                 *args,
                 **kwargs):

        self._params = {} if params is None else params

        if not isinstance(self._params, Mapping):
            raise TypeError(u'Params are not of type dict!')

        super(ParamsDictConfigFrame, self).__init__(*args,
                                                    **kwargs)

    def _draw_param(self,
                    key):

        super(ParamsDictConfigFrame, self)._draw_param(key=key)

        value_entry = TextEntry(frame=self._scroll_frame,
                                value=self._params.get(key, u''),
                                width=self.VALUE_ENTRY_WIDTH,
                                row=Position.CURRENT,
                                column=Position.NEXT,
                                sticky=EW)

        self._param_elements[key] = (self._param_elements[key], value_entry)

    def _perform_delete(self,
                        selected):
        del self._params[selected]
        del self._param_elements[selected]

    def update_params(self):

        for param in self._param_elements:
            param_key = self._param_elements[param][0]
            param_value = self._param_elements[param][1]

            if param_key.value:
                self._params[param_key.value] = param_value.value
