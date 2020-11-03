#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QLabel, QMessageBox, QPlainTextEdit, QTableView, QVBoxLayout, QWidget)

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
        self.sqlEdit = QPlainTextEdit(self.select) # TODO color syntax highlighting
        self.tableModel = TableModel.TableModel(self.db, self.select)
        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        count = self.db.select_row_count(self.select)
        s = 's' if count != 1 else ''
        self.statusLabel = QLabel(f'{count:,} row{s}')
        self.statusLabel.setTextFormat(Qt.RichText)


    def make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.sqlEdit, 2)
        vbox.addWidget(self.tableView, 7)
        vbox.addWidget(self.statusLabel)
        self.setLayout(vbox)


    def make_connections(self):
        pass


    # TODO see PragmaView.py for refresh() & clear()


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
