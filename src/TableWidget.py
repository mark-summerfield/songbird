#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import (
    QLabel, QMessageBox, QTableView, QVBoxLayout, QWidget)

import TableModel


class TableWidget(QWidget):

    def __init__(self, model, kind, name):
        super().__init__()
        self.model = model
        self.name = name
        self.setWindowTitle(name if kind == 'table' else f'{name} ({kind})')
        self.dirty = False
        self.make_widgets(kind)
        self.make_layout()
        self.make_connections()


    def make_widgets(self, kind):
        self.tableModel = TableModel.TableModel(self.model, self.name)
        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        count = self.model.table_row_count(self.name)
        s = 's' if count != 1 else ''
        self.statusLabel = QLabel(f'{count:,} row{s}')


    def make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.tableView, 1)
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
        if self.dirty and bool(self.model):
            # TODO save change to list view or form view
            errors = []# self.model.save_...
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
