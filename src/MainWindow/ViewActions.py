#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMdiArea

import Config
from Ui import make_action

# &View Contents Item
# [X] Show &Contents Tree
# [ ] Show &Items in Tabs|Windows
# [ ] Show &Pragmas
# -------------------
# E&xpand Contents Item  TODO
# C&ollapse Contents Item    TODO
# -------------------
# C&ascade TODO only enable if in MDI mode
# &Tile TODO only enable if in MDI mode
# Ma&ximize TODO only enable if in MDI mode
# Minimi&ze TODO only enable if in MDI mode
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

    def make_view_actions(self):
        path = Config.path() / 'images'
        self.view_view_content_action = make_action(
            self, path / 'window-new.svg', '&View Contents Item',
            self.view_view_content, QKeySequence.AddTab)
        self.view_toggle_action = self.contentsDock.toggleViewAction()
        self.view_toggle_action.setIcon(QIcon(str(path / 'folder.svg')))
        self.view_toggle_action.setText('Show &Contents Tree')
        self.view_toggle_action.toggled.connect(
            self.view_update_toggle_action)
        self.view_toggle_tabs_action = make_action(
            self, path / 'toggletabs.svg', 'Show &Items in Tabs',
            self.view_toggle_tabs)
        self.view_toggle_tabs_action.setCheckable(True)
        self.view_pragmas_toggle_action = (
            self.pragmasDock.toggleViewAction())
        self.view_pragmas_toggle_action.setIcon(QIcon(
            str(path / 'preferences-desktop.svg')))
        self.view_pragmas_toggle_action.setText('Show &Pragmas')
        self.view_pragmas_toggle_action.setChecked(False) # Starts hid
        self.view_pragmas_toggle_action.toggled.connect(
            self.view_pragmas_update_toggle_action)


    def view_update_toggle_action(self, on=None):
        if on is None:
            on = self.contentsDock.isVisible()
        self.view_toggle_action.setText(('Hide' if on else 'Show') +
                                         ' &Contents Tree')


    def view_pragmas_update_toggle_action(self, on=None):
        if on is None:
            on = self.pragmasDock.isVisible()
        self.pragmasDock.widget().setVisible(on)
        self.view_pragmas_toggle_action.setText(
            ('Hide' if on else 'Show') + ' &Pragmas')


    def view_toggle_tabs(self):
        mode = self.mdiArea.viewMode()
        if mode == QMdiArea.TabbedView:
            text = 'Show &Items in Tabs'
            mode = QMdiArea.SubWindowView
            on = False
        else:
            text = 'Show &Items in Windows'
            mode = QMdiArea.TabbedView
            on = True
        self.view_toggle_tabs_action.setText(text)
        self.view_toggle_tabs_action.setChecked(on)
        self.mdiArea.setViewMode(mode)


    @property
    def view_actions_for_menu(self):
        return (self.view_view_content_action, self.view_toggle_action,
                self.view_toggle_tabs_action,
                self.view_pragmas_toggle_action, None)


    @property
    def view_actions_for_toolbar(self):
        return (self.view_view_content_action, self.view_toggle_action,
                self.view_toggle_tabs_action,
                self.view_pragmas_toggle_action, None)


    def view_view_content(self):
        widget = self.contentsDock.widget()
        self.maybe_show_content(widget.currentItem())


    def view_update_ui(self):
        enable = bool(self.db)
        widget = self.contentsDock.widget()
        self.view_view_content_action.setEnabled(
            widget is not None and enable and widget.can_view())
        self.view_pragmas_toggle_action.setEnabled(enable)
