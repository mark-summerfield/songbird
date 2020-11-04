#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

import apsw
import Sql


class TableModel(QAbstractTableModel):

    sql_error = Signal(str)

    def __init__(self, db, sql, parent=None):
        super().__init__(parent)
        self.db = db
        self.sql = sql


    def refresh(self, sql):
        try:
            self.beginResetModel()
            try:
                self.sql = sql
            finally:
                self.endResetModel()
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))


    def rowCount(self, parent=QModelIndex()):
        try:
            return self.db.select_row_count(self.sql)
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))
            return 0


    def columnCount(self, parent=QModelIndex()):
        try:
            return len(Sql.fields_from_select(self.sql))
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))
            return 0


    def data(self, index, role):
        try:
            if (not index.isValid() or
                    index.row() >= self.db.select_row_count(self.sql) or
                    index.column() >=
                    len(Sql.fields_from_select(self.sql))):
                return
            if role == Qt.DisplayRole:
                row = self.db.table_row(self.sql, index.row())
                return row[index.column()]
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))


    def headerData(self, section, orientation, role):
        try:
            if role != Qt.DisplayRole:
                return
            if orientation == Qt.Horizontal:
                return Sql.fields_from_select(self.sql)[section]
            return f'{section + 1:,}'
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))
