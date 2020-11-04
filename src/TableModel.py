#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt

import Sql


class TableModel(QAbstractTableModel):

    def __init__(self, db, select, parent=None):
        super().__init__(parent)
        self.db = db
        self.select = select


    def refresh(self, select):
        self.beginResetModel()
        try:
            self.select = select
        finally:
            self.endResetModel()


    def rowCount(self, parent=QModelIndex()):
        return self.db.select_row_count(self.select)


    def columnCount(self, parent=QModelIndex()):
        return len(Sql.fields_from_select(self.select))


    def data(self, index, role):
        if (not index.isValid() or
                index.row() >= self.db.select_row_count(self.select) or
                index.column() >= len(Sql.fields_from_select(self.select))):
            return None
        if role == Qt.DisplayRole:
            row = self.db.table_row(self.select, index.row())
            return row[index.column()]


    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return Sql.fields_from_select(self.select)[section]
        return f'{section + 1:,}'
