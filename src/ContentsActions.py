#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence

import Config
from Ui import make_action

# [X] Show &Contents
# &View Item
# -------------------
# Toggle &Form View
# &Toggle Tabs
# -------------------
# &Next F6
# &Previous Shift+F6
# &1 <mdi or tab name>
#    :
# &9 <mdi or tab name>
# &More -> &A ... &Z (max 35)
# ---------
# &Close Ctrl+W


class Mixin:

    def make_contents_actions(self):
        path = Config.path()
        self.contents_toggle_action = self.contentsDock.toggleViewAction()
        self.contents_toggle_action.setIcon(QIcon(
            str(path / 'images/folder.svg')))
        self.contents_toggle_action.setText('Show &Contents')
        self.contents_view_content_action = make_action(
            self, path / 'images/window-new.svg', '&View Item',
            self.contents_view_content, QKeySequence.AddTab)


    @property
    def contents_actions_for_menu(self):
        return (self.contents_toggle_action,
                self.contents_view_content_action, )


    @property
    def contents_actions_for_toolbar(self):
        return (self.contents_toggle_action,
                self.contents_view_content_action, )


    def contents_view_content(self):
        view = self.contentsDock.widget()
        if view is not None:
            self.maybe_show_content(view.currentItem())


    def contents_update_ui(self):
        view = self.contentsDock.widget()
        self.contents_view_content_action.setEnabled(
            view is not None and view.can_view())
        print('contents_update_ui') # TODO
