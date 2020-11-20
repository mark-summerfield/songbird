#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import re

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QLabel, QMessageBox, QSplitter, QTableView, QVBoxLayout, QWidget)

import apsw
import TableModel
from Const import APPNAME
from Db import Sql
from SQLEdit import SQLEdit


class TableWidget(QWidget):

    def __init__(self, db, name, select, update_ui):
        super().__init__()
        self.db = db
        self.setWindowTitle(name)
        self.dirty = False
        self.make_widgets(select)
        self.make_layout()
        self.make_connections(update_ui)


    def make_widgets(self, select):
        self.sqlEdit = SQLEdit.SQLEdit(select)
        self.sqlEdit.setTabChangesFocus(True)
        self.tableModel = TableModel.TableModel(self.db,
                                                Sql.uncommented(select))
        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        self.statusLabel = QLabel()
        self.statusLabel.setTextFormat(Qt.RichText)
        self.update_status(select)


    def make_layout(self):
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.sqlEdit)
        self.splitter.addWidget(self.tableView)
        self.splitter.setStretchFactor(1, 11)
        vbox = QVBoxLayout()
        vbox.addWidget(self.splitter)
        vbox.addWidget(self.statusLabel)
        self.setLayout(vbox)


    def make_connections(self, update_ui):
        self.sqlEdit.textChanged.connect(update_ui)
        self.sqlEdit.copyAvailable.connect(update_ui)
        self.tableModel.sql_error.connect(self.on_sql_error)


    @property
    def sizes(self):
        return self.splitter.sizes()


    @property
    def is_select(self):
        select = Sql.uncommented(self.sqlEdit.toPlainText())
        return re.match(r'\s*SELECT\s', select, re.IGNORECASE) is not None


    @property
    def sql(self):
        return self.sqlEdit.toPlainText()


    def refresh(self):
        if not self.is_select:
            self.statusLabel.setText('<font color=red>Only SELECT '
                                     'statements are supported here</font>')
        else:
            select = Sql.uncommented(self.sqlEdit.toPlainText())
            if re.match(r'\s*SELECT(:?\s+(:?ALL|DISTINCT))?\s+\*',
                        select, re.IGNORECASE | re.DOTALL):
                try:
                    names = ', '.join(
                        [Sql.quoted(name) for name in
                        self.db.field_names_for_select(select)])
                    select = select.replace('*', names, 1)
                except apsw.SQLError as err:
                    self.on_sql_error(str(err))
                    return
            self.tableModel.refresh(select)
            self.update_status(select)


    def on_sql_error(self, err):
        self.statusLabel.setText(f'<font color=red>{err}</font>')


    def update_status(self, select):
        try:
            count = self.db.select_row_count(select)
            s = 's' if count != 1 else ''
            self.statusLabel.setText(f'{count:,} row{s}')
        except (apsw.SQLError, Sql.Error) as err:
            self.on_sql_error(str(err))


    def closeEvent(self, event):
        self.save(closing=True)
        event.accept()


    def save(self, *, closing=False):
        print(f'TableWidget.save dirty={self.dirty} closing={closing}')
        saved = False
        errors = False
        if self.dirty and bool(self.db):
            # TODO save change to list view or form view
            errors = []# self.db.save_...
            if errors:
                if not closing:
                    error = '\n'.join(errors)
                    QMessageBox.warning(self, f'Save error — {APPNAME}',
                                        f'Failed to save:\n{error}')
            else:
                saved = True
                self.dirty = False
        return saved
