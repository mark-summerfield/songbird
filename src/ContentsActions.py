#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence

import Config
from Ui import make_action

# [X] Show &Contents
# &View Contents Item
# E&xpand Contents  TODO
# C&ollapse Contents    TODO
# [ ] Show &Pragmas
# -------------------
# Toggle &Form View TODO
# &Toggle Tabs  TODO
# -------------------
# &Next F6  TODO
# &Previous Shift+F6    TODO
# &1 <mdi or tab name>  TODO
#    :
# &9 <mdi or tab name>
# &More -> &A ... &Z (max 35)   TODO
# ---------
# &Close Ctrl+W TODO


class Mixin:

    def make_contents_actions(self):
        path = Config.path()
        self.contents_toggle_action = self.contentsDock.toggleViewAction()
        self.contents_toggle_action.setIcon(QIcon(
            str(path / 'images/folder.svg')))
        self.contents_toggle_action.setText('Show &Contents')
        self.contents_toggle_action.toggled.connect(
            self.contents_update_toggle_action)
        self.contents_view_content_action = make_action(
            self, path / 'images/window-new.svg', '&View Contents Item',
            self.contents_view_content, QKeySequence.AddTab)
        self.pragmas_toggle_action = self.pragmasDock.toggleViewAction()
        self.pragmas_toggle_action.setIcon(QIcon(
            str(path / 'images/preferences-desktop.svg')))
        self.pragmas_toggle_action.setText('Show &Pragmas')
        self.pragmas_toggle_action.toggled.connect(
            self.pragmas_update_toggle_action)


    def contents_update_toggle_action(self, on=None):
        if on is None:
            on = self.contentsDock.isVisible()
        self.contents_toggle_action.setText(('Hide' if on else 'Show') +
                                            ' &Contents')


    def pragmas_update_toggle_action(self, on=None):
        if on is None:
            on = self.pragmasDock.isVisible()
        self.pragmas_toggle_action.setText(('Hide' if on else 'Show') +
                                           ' &Pragmas')


    @property
    def contents_actions_for_menu(self):
        return (self.contents_toggle_action,
                self.contents_view_content_action,
                self.pragmas_toggle_action)


    @property
    def contents_actions_for_toolbar(self):
        return (self.contents_toggle_action,
                self.contents_view_content_action,
                self.pragmas_toggle_action)


    def contents_view_content(self):
        view = self.contentsDock.widget()
        if view is not None:
            self.maybe_show_content(view.currentItem())


    def contents_update_ui(self):
        enable = bool(self.model)
        view = self.contentsDock.widget()
        self.contents_view_content_action.setEnabled(
            view is not None and enable and view.can_view())
