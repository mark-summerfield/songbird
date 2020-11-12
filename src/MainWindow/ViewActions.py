#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMdiArea

import Config
from Ui import make_action

# &Show Item
# [X] Show Items &Tree
# [ ] Show &Items in Tabs|Windows
# [ ] Show &Pragmas
# -------------------
# E&xpand Tree Item  TODO
# C&ollapse Tree Item    TODO
# -------------------
# C&ascade TODO only enable if in MDI mode
# &Tile TODO only enable if in MDI mode
# Ma&ximize TODO only enable if in MDI mode
# Minimi&ze TODO only enable if in MDI mode
# -------------------
# &Next F6  TODO
# &Previous Shift+F6    TODO
# &1 <mdi or tab name>  TODO -or- Window|Tab submenu &A..&Z (max 26)
#    :
# &9 <mdi or tab name>
# &More -> &A ... &Z (max 35)   TODO
# ---------
# &Close Ctrl+W TODO


class Mixin:

    def make_view_actions(self):
        path = Config.path() / 'images'
        self.view_show_item_action = make_action(
            self, path / 'window-new.svg', '&Show Item',
            self.view_show_item, QKeySequence.AddTab)
        self.view_items_tree_toggle_action = (
            self.itemsTreeDock.toggleViewAction())
        self.view_items_tree_toggle_action.setIcon(
            QIcon(str(path / 'folder.svg')))
        self.view_items_tree_toggle_action.setText('Show Items &Tree')
        self.view_items_tree_toggle_action.toggled.connect(
            self.view_update_toggle_action)
        self.view_items_tree_toggle_tabs_action = make_action(
            self, path / 'toggletabs.svg', 'Show &Items in Tabs',
            self.view_items_tree_toggle_tabs)
        self.view_items_tree_toggle_tabs_action.setCheckable(True)
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
            on = self.itemsTreeDock.isVisible()
        self.view_items_tree_toggle_action.setText(
            ('Hide' if on else 'Show') + ' Items &Tree')


    def view_pragmas_update_toggle_action(self, on=None):
        if on is None:
            on = self.pragmasDock.isVisible()
        self.pragmasDock.widget().setVisible(on)
        self.view_pragmas_toggle_action.setText(
            ('Hide' if on else 'Show') + ' &Pragmas')


    def view_items_tree_toggle_tabs(self):
        mode = self.mdiArea.viewMode()
        if mode == QMdiArea.TabbedView:
            text = 'Show &Items in Tabs'
            mode = QMdiArea.SubWindowView
            on = False
        else:
            text = 'Show &Items in Windows'
            mode = QMdiArea.TabbedView
            on = True
        self.view_items_tree_toggle_tabs_action.setText(text)
        self.view_items_tree_toggle_tabs_action.setChecked(on)
        self.mdiArea.setViewMode(mode)


    @property
    def view_actions_for_menu(self):
        return (self.view_show_item_action,
                self.view_items_tree_toggle_action,
                self.view_items_tree_toggle_tabs_action,
                self.view_pragmas_toggle_action, None)


    @property
    def view_actions_for_toolbar(self):
        return (self.view_show_item_action,
                self.view_items_tree_toggle_action,
                self.view_items_tree_toggle_tabs_action,
                self.view_pragmas_toggle_action, None)


    def view_show_item(self):
        widget = self.itemsTreeDock.widget()
        self.maybe_show_item(widget.currentItem())


    def view_update_ui(self):
        enable = bool(self.db)
        widget = self.itemsTreeDock.widget()
        self.view_show_item_action.setEnabled(
            widget is not None and enable and widget.can_view())
        self.view_pragmas_toggle_action.setEnabled(enable)
