# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from . import (ParamsUITypesConstant,
               ParamsDictConfigFrame,
               ParamsListConfigFrame)

logging = logging_helper.setup_logging()


class ParamsConfigWindow(ChildWindow):

    def __init__(self,
                 params=None,
                 params_type=ParamsUITypesConstant.dict,
                 *args,
                 **kwargs):

        self._params = params
        self._params_type = params_type

        super(ParamsConfigWindow, self).__init__(*args,
                                                 **kwargs)

    def _draw_widgets(self):
        self.title(u"Edit Params")

        if self._params_type == ParamsUITypesConstant.dict:
            self.config = ParamsDictConfigFrame(params=self._params,
                                                sticky=NSEW)

        elif self._params_type == ParamsUITypesConstant.list:
            self.config = ParamsListConfigFrame(params=self._params,
                                                sticky=NSEW)

        else:
            raise TypeError(u'Unknown params type: {t}'.format(t=self._params_type))

    def close(self):
        self.config.update_params()

    @property
    def params(self):
        return self.config.params
