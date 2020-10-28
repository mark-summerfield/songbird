#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QKeySequence

import Config
from Ui import make_action


class Mixin:

    def make_edit_actions(self):
        path = Config.path()
        self.edit_copy_action = make_action(
            self, path / 'images/edit-copy.svg', '&Copy', self.edit_copy,
            QKeySequence.Copy)
        self.edit_cut_action = make_action(
            self, path / 'images/edit-cut.svg', 'C&ut', self.edit_cut,
            QKeySequence.Cut)
        self.edit_paste_action = make_action(
            self, path / 'images/edit-paste.svg', '&Paste', self.edit_paste,
            QKeySequence.Paste)


    @property
    def edit_actions_for_menu(self):
        return (self.edit_copy_action, self.edit_cut_action,
                self.edit_paste_action)


    @property
    def edit_actions_for_toolbar(self):
        return (self.edit_copy_action, self.edit_cut_action,
                self.edit_paste_action)


    def edit_update_ui(self):
        for action in (self.edit_copy_action, self.edit_cut_action,
                       self.edit_paste_action):
            action.setEnabled(False)
        widget = qApp.focusWidget()
        if widget is None:
            self.edit_copy_action.setEnabled(
                self.contentsDock.widget().canCopy())
            # TODO if calendar then copy date?
        else:
            try:
                self.edit_paste_action.setEnabled(widget.canPaste())
            except AttributeError:
                pass # Already set to False
            try:
                text_cursor = widget.textCursor()
                enable = text_cursor.hasSelection()
                self.edit_copy_action.setEnabled(enable)
                self.edit_cut_action.setEnabled(enable)
            except AttributeError:
                pass # Already set to False


    def edit_copy(self):
        widget = qApp.focusWidget()
        if widget is not None:
            try:
                widget.copy()
            except AttributeError:
                pass # Not supported by this widget


    def edit_cut(self):
        widget = qApp.focusWidget()
        if widget is not None:
            try:
                widget.cut()
            except AttributeError:
                pass # Not supported by this widget


    def edit_paste(self):
        widget = qApp.focusWidget()
        if widget is not None:
            try:
                widget.paste()
            except AttributeError:
                pass # Not supported by this widget
