#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QLabel, QMessageBox, QSplitter, QTableView, QVBoxLayout, QWidget)

import SQLEdit
import TableModel


class TableWidget(QWidget):

    def __init__(self, db, name, select):
        super().__init__()
        self.db = db
        self.setWindowTitle(name)
        self.dirty = False
        self.make_widgets(select)
        self.make_layout()
        self.make_connections()


    def make_widgets(self, select):
        self.sqlEdit = SQLEdit.SQLEdit(select)
        self.sqlEdit.setTabChangesFocus(True)
        # TODO color syntax highlighting
        self.tableModel = TableModel.TableModel(self.db, select)
        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        self.statusLabel = QLabel()
        self.statusLabel.setTextFormat(Qt.RichText)
        self.update_status(select)


    def make_layout(self):
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.sqlEdit)
        splitter.addWidget(self.tableView)
        splitter.setStretchFactor(1, 11)
        vbox = QVBoxLayout()
        vbox.addWidget(splitter)
        vbox.addWidget(self.statusLabel)
        self.setLayout(vbox)


    def make_connections(self):
        pass


    def refresh(self):
        select = self.sqlEdit.toPlainText()
        err = self.db.check_select(select)
        if not err:
            self.tableModel.refresh(select)
            self.update_status(select)
        else:
            self.statusLabel.setText(f'<font color=red>{err}</font>')


    def update_status(self, select):
        count = self.db.select_row_count(select)
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
