# encoding: utf-8

import logging_helper
from copy import deepcopy
from uiutil import Button
from . import (ParamsUITypesConstant,
               ParamsConfigWindow)

logging = logging_helper.setup_logging()


class ParamsConfigButton(Button):

    def __init__(self,
                 frame,
                 params,
                 params_type=ParamsUITypesConstant.dict,
                 tooltip=True,
                 *args,
                 **kwargs):

        """ Custom button used for editing passed in params

        :param params:      object containing params to be configured or a callable function
                             that will return the object.
        :param params_type: data type of the params.  See ParamsUITypesConstant.
        :param tooltip:     True to enable tooltip display of current params.
        :param args:        Do not pass positional arguments.
        :param kwargs:
        """

        self._params_var = params
        self._params = None
        self._params_type = params_type
        self._enable_tooltip = tooltip
        self._frame = frame

        kwargs[u'command'] = self._edit_params

        if u'text' not in kwargs:
            kwargs[u'text'] = u'Edit Params'

        if self._enable_tooltip:
            kwargs[u'tooltip'] = self._tooltip_kwargs

        super(Button, self).__init__(*args,
                                     **kwargs)

        self.update_params()

    def _edit_params(self):

        window = ParamsConfigWindow(params=self.update_params(),
                                    params_type=self._params_type,
                                    fixed=True,
                                    parent_geometry=self._frame.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self._frame.wait_window(window)

        self._params = window.params

    def _tooltip_kwargs(self):

        string = u'No parameters configured'

        if self._params is not None:
            if len(self._params) > 1:
                if self._params_type == ParamsUITypesConstant.dict:
                    string = u'{\n'

                    for param in sorted(self._params):
                        string += u' {k}: {v}\n'.format(k=param,
                                                        v=self._params[param])

                    string += u'}'

                if self._params_type == ParamsUITypesConstant.list:
                    string = u'[\n'

                    for param in self._params:
                        string += u' {k}\n'.format(k=param)

                    string += u']'

            elif len(self._params) == 1:
                string = str(self._params)

        return {
            u'text': string,
            u'justify': u'left'
        }

    def update_params(self):
        self._params = deepcopy(self._params_var() if callable(self._params_var) else self._params_var)
        return self._params

    @property
    def params(self):
        return self._params
