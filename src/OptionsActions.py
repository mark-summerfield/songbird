#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence

import Config
from Ui import make_action


class Mixin:

    def make_options_actions(self):
        path = Config.path()
        self.options_toggle_contents_action = (
            self.contentsDock.toggleViewAction())
        self.options_toggle_contents_action.setIcon(
            QIcon(str(path / 'images/folder.svg')))
        self.options_toggle_contents_action.setText('Show &Contents')
        # TODO


    @property
    def options_actions_for_menu(self):
        # TODO
        return (self.options_toggle_contents_action,)


    @property
    def options_actions_for_toolbar(self):
        # TODO
        return (self.options_toggle_contents_action,)


    def options_update_ui(self):
        # TODO
        pass
