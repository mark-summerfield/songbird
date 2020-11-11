#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMdiArea

import Config
from Ui import make_action

# &View Contents Item
# [X] Show &Contents
# [ ] Show &As Tabs|Windows
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

    def make_contents_actions(self):
        path = Config.path() / 'images'
        self.contents_view_content_action = make_action(
            self, path / 'window-new.svg', '&View Contents Item',
            self.contents_view_content, QKeySequence.AddTab)
        self.contents_toggle_action = self.contentsDock.toggleViewAction()
        self.contents_toggle_action.setIcon(QIcon(str(path / 'folder.svg')))
        self.contents_toggle_action.setText('Show &Contents')
        self.contents_toggle_action.toggled.connect(
            self.contents_update_toggle_action)
        self.contents_toggle_tabs_action = make_action(
            self, path / 'toggletabs.svg', 'Show &As Tabs',
            self.contents_toggle_tabs)
        self.contents_toggle_tabs_action.setCheckable(True)
        self.contents_pragmas_toggle_action = (
            self.pragmasDock.toggleViewAction())
        self.contents_pragmas_toggle_action.setIcon(QIcon(
            str(path / 'preferences-desktop.svg')))
        self.contents_pragmas_toggle_action.setText('Show &Pragmas')
        self.contents_pragmas_toggle_action.setChecked(False) # Starts hid
        self.contents_pragmas_toggle_action.toggled.connect(
            self.contents_pragmas_update_toggle_action)


    def contents_update_toggle_action(self, on=None):
        if on is None:
            on = self.contentsDock.isVisible()
        self.contents_toggle_action.setText(('Hide' if on else 'Show') +
                                            ' &Contents')


    def contents_pragmas_update_toggle_action(self, on=None):
        if on is None:
            on = self.pragmasDock.isVisible()
        self.pragmasDock.widget().setVisible(on)
        self.contents_pragmas_toggle_action.setText(
            ('Hide' if on else 'Show') + ' &Pragmas')


    def contents_toggle_tabs(self):
        mode = self.mdiArea.viewMode()
        if mode == QMdiArea.TabbedView:
            text = 'Show &As Tabs'
            mode = QMdiArea.SubWindowView
            on = False
        else:
            text = 'Show &As Windows'
            mode = QMdiArea.TabbedView
            on = True
        self.contents_toggle_tabs_action.setText(text)
        self.contents_toggle_tabs_action.setChecked(on)
        self.mdiArea.setViewMode(mode)


    @property
    def contents_actions_for_menu(self):
        return (self.contents_view_content_action,
                self.contents_toggle_action,
                self.contents_toggle_tabs_action,
                self.contents_pragmas_toggle_action, None)


    @property
    def contents_actions_for_toolbar(self):
        return (self.contents_view_content_action,
                self.contents_toggle_action,
                self.contents_toggle_tabs_action,
                self.contents_pragmas_toggle_action, None)


    def contents_view_content(self):
        widget = self.contentsDock.widget()
        self.maybe_show_content(widget.currentItem())


    def contents_update_ui(self):
        enable = bool(self.db)
        widget = self.contentsDock.widget()
        self.contents_view_content_action.setEnabled(
            widget is not None and enable and widget.can_view())
        self.contents_pragmas_toggle_action.setEnabled(enable)
