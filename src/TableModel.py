#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt


class TableModel(QAbstractTableModel):

    def __init__(self, db, name, parent=None):
        super().__init__(parent)
        self.db = db
        self.name = name # SQL table or view name


    def rowCount(self, parent=QModelIndex()):
        return self.db.table_row_count(self.name)


    def columnCount(self, parent=QModelIndex()):
        return self.db.table_field_count(self.name)


    def data(self, index, role):
        if (not index.isValid() or
                index.row() >= self.db.table_row_count(self.name) or
                index.column() >= self.db.table_field_count(self.name)):
            return None
        if role == Qt.DisplayRole:
            return self.db.table_item(self.name, index.row(),
                                      index.column())


    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self.db.table_field_for_column(self.name, section)
        return f'{section + 1:,}'

    # TODO make editable
