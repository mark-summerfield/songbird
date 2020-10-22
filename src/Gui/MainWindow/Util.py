#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.


from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QToolBar, QToolButton


def make_action(widget, icon, text, slot=None, shortcut=None, tooltip=None,
                *, menu=None):
    action = QAction(QIcon(str(icon)), text, widget)
    if slot is not None:
        action.triggered.connect(slot)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tooltip is not None:
        action.setToolTip(tooltip)
    if menu is not None:
        action.setMenu(menu)
    return action


def add_actions(menu_or_toolbar, actions):
    is_toolbar = isinstance(menu_or_toolbar, QToolBar)
    for action in actions:
        if action is None:
            menu_or_toolbar.addSeparator()
        elif is_toolbar and action.menu() is not None:
            button = QToolButton()
            button.setDefaultAction(action)
            button.setPopupMode(QToolButton.InstantPopup)
            menu_or_toolbar.addWidget(button)
        else:
            menu_or_toolbar.addAction(action)


def create_tool_button(icon, tooltip, slot=None, *, menu=None):
    button = QToolButton()
    button.setToolTip(tooltip)
    button.setIcon(QIcon(icon))
    if slot is not None:
        button.clicked.connect(slot)
    if menu is not None:
        button.setPopupMode(QToolButton.InstantPopup)
        button.setMenu(menu)
    return button
