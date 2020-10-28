#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence

import Config
from Ui import make_action

# [X] Show &Toolbar
# [ ] Show C&alendar
# &Options...


class Mixin:

    def make_options_actions(self):
        path = Config.path()
        # TODO


    @property
    def options_actions_for_menu(self):
        # TODO
        return ()


    @property
    def options_actions_for_toolbar(self):
        # TODO
        return ()


    def options_update_ui(self):
        # TODO
        pass
