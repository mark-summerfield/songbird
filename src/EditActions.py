#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import re

from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import (
    QLineEdit, QMdiSubWindow, QPlainTextEdit, QTextEdit)

import apsw
import Config
import Sql
from Ui import make_action


class Mixin:

    def make_edit_actions(self):
        path = Config.path() / 'images'
        self.edit_refresh_action = make_action(
            self, path / 'view-refresh.svg', '&Refresh', self.edit_refresh,
            QKeySequence.Refresh)
        self.edit_replace_star_action = make_action(
            self, path / 'format-indent-more.svg', "Replace &SELECT's *",
            self.edit_replace_star)
        self.edit_copy_action = make_action(
            self, path / 'edit-copy.svg', '&Copy', self.edit_copy,
            QKeySequence.Copy)
        self.edit_cut_action = make_action(
            self, path / 'edit-cut.svg', 'C&ut', self.edit_cut,
            QKeySequence.Cut)
        self.edit_paste_action = make_action(
            self, path / 'edit-paste.svg', '&Paste', self.edit_paste,
            QKeySequence.Paste)


    @property
    def edit_actions_for_menu(self):
        return (self.edit_refresh_action, None,
                self.edit_replace_star_action, None, self.edit_copy_action,
                self.edit_cut_action, self.edit_paste_action)


    @property
    def edit_actions_for_toolbar(self):
        return (self.edit_refresh_action, None,
                self.edit_replace_star_action, None, self.edit_copy_action,
                self.edit_cut_action, self.edit_paste_action)


    def edit_update_ui(self):
        enable = bool(self.db)
        self.edit_refresh_action.setEnabled(enable)
        for action in (self.edit_replace_star_action, self.edit_copy_action,
                       self.edit_cut_action, self.edit_paste_action):
            action.setEnabled(False)
        widget = qApp.focusWidget()
        if isinstance(widget, QLineEdit):
            hasText = widget.selectionLength() > 0
            self.edit_copy_action.setEnabled(hasText)
            self.edit_cut_action.setEnabled(hasText)
            clipboard = qApp.clipboard()
            self.edit_paste_action.setEnabled(bool(clipboard.text()))
        elif isinstance(widget, (QPlainTextEdit, QTextEdit)):
            if enable: 
                if sql := widget.toPlainText().strip():
                    sql = Sql.uncommented(sql)
                    if re.match(r'\s*SELECT(:?\s+(:?ALL|DISTINCT))?\s+\*',
                                sql, re.IGNORECASE):
                        self.edit_replace_star_action.setEnabled(True)
            text_cursor = widget.textCursor()
            enable = text_cursor.hasSelection()
            self.edit_copy_action.setEnabled(enable)
            self.edit_cut_action.setEnabled(enable)
            self.edit_paste_action.setEnabled(widget.canPaste())


    def edit_refresh(self):
        widget = qApp.focusWidget()
        while widget is not None:
            if isinstance(widget, QMdiSubWindow):
                widget.widget().refresh()
                break
            widget = widget.parent()


    def edit_replace_star(self):
        widget = qApp.focusWidget()
        if widget is not None and isinstance(widget, (QPlainTextEdit,
                                                      QTextEdit)):
            select = widget.toPlainText()
            try:
                names = ', '.join([Sql.quoted(name) for name in
                                  self.db.field_names_for_select(select)])
                widget.setPlainText(re.sub(
                    r'(SELECT(:?\s+(:?ALL|DISTINCT))?\s)\s*\*',
                    lambda match: match.group(1).upper() + names,
                    widget.toPlainText(), flags=re.IGNORECASE))
            except apsw.SQLError as err:
                while widget is not None and not isinstance(widget,
                                                            QMdiSubWindow):
                    widget = widget.parent()
                if widget is not None:
                    widget.widget().on_sql_error(str(err))


    def edit_copy(self):
        if (widget := qApp.focusWidget()) is not None:
            try:
                widget.copy()
            except AttributeError:
                pass # Not supported by this widget


    def edit_cut(self):
        if (widget := qApp.focusWidget()) is not None:
            try:
                widget.cut()
            except AttributeError:
                pass # Not supported by this widget


    def edit_paste(self):
        if (widget := qApp.focusWidget()) is not None:
            try:
                widget.paste()
            except AttributeError:
                pass # Not supported by this widget
