# encoding: utf-8

import logging_helper
from uiutil.tk_names import EW
from uiutil import BaseLabelFrame, Button, Position

logging = logging_helper.setup_logging()


class ConfigLauncherFrame(BaseLabelFrame):

    BUTTON_WIDTH = 12

    def __init__(self,
                 config_windows,
                 *args,
                 **kwargs):

        super(ConfigLauncherFrame, self).__init__(*args,
                                                  **kwargs)

        self._config_windows = config_windows

        self._draw_buttons()
        self.nice_grid()

    def _draw_buttons(self):

        for window in self._config_windows:
            Button(text=window[u'name'],
                   width=self.BUTTON_WIDTH,
                   row=Position.START,
                   column=Position.START if self._config_windows.index(window) == 0 else Position.NEXT,
                   sticky=EW,
                   command=lambda window_class=window[u'class']: self.launch_config_window(window_class))

    def launch_config_window(self,
                             window):
        window(fixed=True,
               parent_geometry=self.parent.winfo_toplevel().winfo_geometry())
