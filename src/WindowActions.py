#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QKeySequence

import Config
from Ui import make_action


class Mixin:

    def make_window_actions(self):
        path = Config.path()
        self.window_view_content_action = make_action(
            self, path / 'images/window-new.svg', '&View Content Item',
            self.window_view_content)
        # TODO add tooltip that this is new from the current content item


    @property
    def window_actions_for_menu(self):
        return (self.window_view_content_action,)


    @property
    def window_actions_for_toolbar(self):
        return (self.window_view_content_action,)


    def window_view_content(self):
        view = self.contentsDock.widget()
        if view is not None:
            self.maybe_show_content(view.currentItem())
