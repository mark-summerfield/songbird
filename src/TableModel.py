#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

import apsw
import Sql


class TableModel(QAbstractTableModel):

    sql_error = Signal(str)

    def __init__(self, db, select, parent=None):
        super().__init__(parent)
        self.db = db
        self.select = select


    def refresh(self, select):
        try:
            self.beginResetModel()
            try:
                self.select = select
            finally:
                self.endResetModel()
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))


    def rowCount(self, parent=QModelIndex()):
        try:
            return self.db.select_row_count(self.select)
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))
            return 0


    def columnCount(self, parent=QModelIndex()):
        try:
            try:
                return Sql.field_count_from_select(self.select)
            except Sql.Error:
                return len(self.db.field_names_for_select(self.select))
        except apsw.SQLError as err:
            self.sql_error.emit(str(err))
            return 0


    def data(self, index, role):
        try:
            if (not index.isValid() or index.row() >= self.rowCount() or
                    index.column() >= self.columnCount()):
                return
            if role == Qt.DisplayRole:
                row = self.db.table_row(self.select, index.row())
                return row[index.column()]
        except (apsw.SQLError, Sql.Error) as err:
            self.sql_error.emit(str(err))


    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            try:
                try:
                    names = Sql.field_names_from_select(self.select)
                except Sql.Error:
                    names = self.db.field_names_for_select(self.select)
                return names[section]
            except apsw.SQLError as err:
                self.sql_error.emit(str(err))
        return f'{section + 1:,}'
