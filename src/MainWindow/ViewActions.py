#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMdiArea

from AppData import (
    FOLDER_SVG, PREFERENCES_DESKTOP_SVG, TOGGLETABS_SVG, WINDOW_NEW_SVG,
    get_icon)
from Ui import make_action

# &Show Item
# [X] Show Items &Tree
# [ ] Show &Items in Tabs|Windows
# [ ] Show &Pragmas
# [ ] Show Ca&lendar TODO
# -------------------
# E&xpand Tree Item  TODO
# C&ollapse Tree Item    TODO
# -------------------
# &Goto Item Tree TODO
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
        self.view_show_item_action = make_action(
            self, get_icon(WINDOW_NEW_SVG), '&Show Item',
            self.view_show_item, QKeySequence.AddTab,
            "Show the current item tree's item either by creating a tab "
            'or window or by bringing an existing tab or window to the '
            'front')
        self.view_items_tree_toggle_action = (
            self.itemsTreeDock.toggleViewAction())
        self.view_items_tree_toggle_action.setIcon(get_icon(FOLDER_SVG))
        self.view_items_tree_toggle_action.setText('Show Items &Tree')
        tip = 'Show or hide the tree of queries and database items'
        self.view_items_tree_toggle_action.setToolTip(tip)
        self.view_items_tree_toggle_action.setStatusTip(tip)
        self.view_items_tree_toggle_action.toggled.connect(
            self.view_update_toggle_action)
        self.view_items_tree_toggle_tabs_action = make_action(
            self, get_icon(TOGGLETABS_SVG), 'Show &Items in Tabs',
            self.view_items_tree_toggle_tabs)
        self.view_items_tree_toggle_tabs_action.setCheckable(True)
        tip = 'Show items in tabs or in windows' 
        self.view_items_tree_toggle_tabs_action.setToolTip(tip)
        self.view_items_tree_toggle_tabs_action.setStatusTip(tip)
        self.view_pragmas_toggle_action = (
            self.pragmasDock.toggleViewAction())
        self.view_pragmas_toggle_action.setIcon(
            get_icon(PREFERENCES_DESKTOP_SVG))
        self.view_pragmas_toggle_action.setText('Show &Pragmas')
        self.view_pragmas_toggle_action.setChecked(False) # Starts hid
        tip = "Show or hide the database's pragmas"
        self.view_pragmas_toggle_action.setToolTip(tip)
        self.view_pragmas_toggle_action.setStatusTip(tip)
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
            what = 'Tabs'
            mode = QMdiArea.SubWindowView
            on = False
        else:
            what = 'Windows'
            mode = QMdiArea.TabbedView
            on = True
        self.view_items_tree_toggle_tabs_action.setText(
            f'Show &Items in {what}')
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
