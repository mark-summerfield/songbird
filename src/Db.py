#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import functools

import apsw
from Const import UNCHANGED
from Sql import (
    CONTENT_DETAIL, CONTENT_SUMMARY, TABLE_FIELD_COUNT,
    TABLE_FIELD_FOR_COLUMN, TABLE_ITEM, TABLE_ROW_COUNT, ContentDetail,
    ContentSummary, Pragmas, first)


class Db:

    def __init__(self, filename=None):
        self._db = None
        if filename is None:
            self._filename = None
        else:
            self.open(filename)


    def __bool__(self):
        return self._db is not None


    @property
    def filename(self):
        return self._filename


    def open(self, filename):
        self.close()
        self._filename = filename
        self._db = apsw.Connection(str(filename))


    def close(self):
        if self._db is not None:
            self._db.close()
            self._db = None
        self._filename = None
        self.refresh()


    def refresh(self):
        self.table_field_for_column.cache_clear()
        self.table_field_count.cache_clear()


    def content_summary(self):
        if self._db is not None:
            cursor = self._db.cursor()
            for row in cursor.execute(CONTENT_SUMMARY):
                content = ContentSummary(*row)
                if content.name.startswith(('sqlite_', 'songbird')):
                    continue
                yield content


    def content_detail(self, name):
        if self._db is not None:
            cursor = self._db.cursor()
            for row in cursor.execute(CONTENT_DETAIL, dict(name=name)):
                row = list(row[1:])
                row.pop(3)
                yield ContentDetail(*row)


    def pragmas(self):
        pragmas = Pragmas()
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                pragmas.user_version = first(
                    cursor, 'PRAGMA user_version', default=0)
        return pragmas


    def pragmas_save(self, pragmas):
        errors = []
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                if pragmas.user_version is not UNCHANGED:
                    try:
                        cursor.execute(
                            f'PRAGMA user_version = {pragmas.user_version}')
                    except apsw.SQLError as err:
                        errors.append(str(err))
        return errors


    def table_row_count(self, name): # No cache because it changes too much
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                return first(cursor, TABLE_ROW_COUNT.format(name=name),
                             default=0)
        return 0


    @functools.lru_cache
    def table_field_count(self, name):
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                return first(cursor, TABLE_FIELD_COUNT, dict(name=name),
                             default=0)
        return 0


    # TODO delete
    def table_item(self, name, row, column):
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                field = self.table_field_for_column(name, column)
                sql = TABLE_ITEM.format(name=name, field=field, row=row)
                return first(cursor, sql, Class=str)
        return None


    # TODO delete
    @functools.lru_cache
    def table_field_for_column(self, name, column):
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                return first(cursor, TABLE_FIELD_FOR_COLUMN,
                             dict(name=name, row=column), Class=str)
