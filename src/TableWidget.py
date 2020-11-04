#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QHBoxLayout, QLabel, QMessageBox, QSplitter, QTableView,
    QVBoxLayout, QWidget)

import SQLEdit
import SQLLineEdit
import TableModel


class TableWidget(QWidget):

    def __init__(self, db, kind, name, select):
        super().__init__()
        self.db = db
        self.setWindowTitle(f'{name} — {kind}')
        self.select = select
        self.dirty = False
        self.make_widgets()
        self.make_layout()
        self.make_connections()


    def make_widgets(self):
        self.sqlEdit = SQLEdit.SQLEdit(self.select)
        self.sqlEdit.setReadOnly(True)
        self.sqlEdit.setTabChangesFocus(True)
        self.whereEdit = SQLLineEdit.SQLLineEdit()
        self.whereEdit.setPlaceholderText('WHERE')
        self.orderByEdit = SQLLineEdit.SQLLineEdit()
        self.orderByEdit.setPlaceholderText('ORDER BY')
        # TODO color syntax highlighting
        self.tableModel = TableModel.TableModel(self.db, self.select)
        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        self.statusLabel = QLabel()
        self.statusLabel.setTextFormat(Qt.RichText)
        self.update_status()


    def make_layout(self):
        editorVbox = QVBoxLayout()
        editorVbox.addWidget(self.sqlEdit)
        hbox = QHBoxLayout()
        hbox.addWidget(self.whereEdit)
        hbox.addWidget(self.orderByEdit)
        editorVbox.addLayout(hbox)
        widget = QWidget()
        widget.setLayout(editorVbox)
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(widget)
        splitter.addWidget(self.tableView)
        splitter.setStretchFactor(1, 11)
        vbox = QVBoxLayout()
        vbox.addWidget(splitter)
        vbox.addWidget(self.statusLabel)
        self.setLayout(vbox)


    def make_connections(self):
        pass


    def refresh(self):
        where = self.whereEdit.text()
        if where:
            where = where.strip()
            if where:
                if not where.upper().startswith('WHERE '):
                    where = f' WHERE {where}'
        order_by = self.orderByEdit.text()
        if order_by:
            order_by = order_by.strip()
            if order_by:
                if not order_by.upper().startswith('ORDER BY '):
                    order_by = f' ORDER BY {order_by}'
        self.select = self.sqlEdit.toPlainText() + where + order_by
        err = self.db.check_select(self.select)
        if not err:
            self.tableModel.refresh(self.select)
            self.update_status()
        else:
            self.statusLabel.setText(f'<font color=red>{err}</font>')


    def update_status(self):
        count = self.db.select_row_count(self.select)
        s = 's' if count != 1 else ''
        self.statusLabel.setText(f'{count:,} row{s}')


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
                    QMessageBox.warning(
                        self, f'Save error — {qApp.applicationName()}',
                        f'Failed to save:\n{error}')
            else:
                saved = True
                self.dirty = False
        return saved
