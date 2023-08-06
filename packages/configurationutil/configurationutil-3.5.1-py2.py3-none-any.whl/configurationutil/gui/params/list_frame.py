# encoding: utf-8

from . import ParamsBaseConfigFrame


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
