#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import functools

import apsw
from Const import UNCHANGED
from Sql import (
    CONTENT_DETAIL, CONTENT_SUMMARY, TABLE_FIELD_COUNT, TABLE_FIELDS,
    TABLE_ITEM, TABLE_ROW_COUNT, ContentDetail, ContentSummary, Pragmas,
    first)


class Model:

    def __init__(self, filename=None):
        self.db = None
        if filename is None:
            self._filename = None
        else:
            self.open(filename)


    def __bool__(self):
        return self.db is not None


    @property
    def filename(self):
        return self._filename


    def open(self, filename):
        self.close()
        self._filename = filename
        self.db = apsw.Connection(str(filename))


    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        self._filename = None
        self.refresh()


    def refresh(self):
        self.table_field_for_column.cache_clear()
        self.table_field_count.cache_clear()


    def content_summary(self):
        if self.db is not None:
            cursor = self.db.cursor()
            for row in cursor.execute(CONTENT_SUMMARY):
                content = ContentSummary(*row)
                if content.name.startswith(('sqlite_', 'songbird')):
                    continue
                yield content


    def content_detail(self, name):
        if self.db is not None:
            cursor = self.db.cursor()
            for row in cursor.execute(CONTENT_DETAIL, dict(name=name)):
                row = list(row[1:])
                row.pop(3)
                yield ContentDetail(*row)


    def pragmas(self):
        pragmas = Pragmas()
        if self.db is not None:
            cursor = self.db.cursor()
            with self.db:
                pragmas.user_version = first(
                    cursor, 'PRAGMA user_version', default=0)
        return pragmas


    def save_pragmas(self, pragmas):
        errors = []
        if self.db is not None:
            cursor = self.db.cursor()
            with self.db:
                if pragmas.user_version is not UNCHANGED:
                    try:
                        cursor.execute(
                            f'PRAGMA user_version = {pragmas.user_version}')
                    except apsw.SQLError as err:
                        errors.append(str(err))
        return errors


    def table_row_count(self, name): # No cache because it changes too much
        if self.db is not None:
            cursor = self.db.cursor()
            with self.db:
                return first(cursor, TABLE_ROW_COUNT.format(name=name),
                             default=0)
        return 0


    @functools.lru_cache
    def table_field_count(self, name):
        if self.db is not None:
            cursor = self.db.cursor()
            with self.db:
                return first(cursor, TABLE_FIELD_COUNT, dict(name=name),
                             default=0)
        return 0


    def table_item(self, name, row, column):
        if self.db is not None:
            cursor = self.db.cursor()
            with self.db:
                field = self.table_field_for_column(name, column)
                sql = TABLE_ITEM.format(name=name, field=field, row=row)
                return first(cursor, sql, Class=str)
        return None


    @functools.lru_cache
    def table_field_for_column(self, name, column):
        if self.db is not None:
            cursor = self.db.cursor()
            with self.db:
                return first(cursor, TABLE_FIELDS,
                             dict(name=name, row=column), Class=str)
