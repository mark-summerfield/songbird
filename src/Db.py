#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import functools
import re

import apsw
from Const import UNCHANGED
from Sql import (
    CONTENT_DETAIL, CONTENT_SUMMARY, TABLE_OR_VIEW_SQL, ContentDetail,
    ContentSummary, Pragmas, first, select_from_create_view)


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
        self.table_make_select.cache_clear()
        self.view_make_select.cache_clear()


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
                yield ContentDetail(*row[1:])


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


    def select_make(self, kind, name):
        if kind == 'view':
            return self.view_make_select(name)
        elif kind == 'table':
            return self.table_make_select(name)
        # return self.query_make_select(name) # TODO


    def select_row_count(self, select):
        select.rstrip(';')
        sql = f'SELECT COUNT(*) FROM ({select})'
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                return first(cursor, sql, default=0)
        return 0


    @functools.lru_cache
    def table_make_select(self, name):
        fields = []
        for detail in self.content_detail(name):
            fields.append(detail.name)
        fields = ', '.join(fields)
        return f'SELECT {fields} FROM {name}'


    def table_row(self, select, row): # Rely on SQLite to cache
        limit_rx = re.compile(
            r'\sLIMIT\s+\d+(:?\s+OFFSET\s+(?P<offset>\d+))?', re.IGNORECASE)
        if self._db is not None:
            match = limit_rx.search(select)
            if match is None: # No limit set
                sql = select.rstrip(';') + ' LIMIT 1'
            else:
                offset = match.group('offset')
                if offset:
                    row += int(offset)
                sql = limit_rx.sub(' LIMIT 1', select)
            sql += f' OFFSET {row}'
            cursor = self._db.cursor()
            with self._db:
                return cursor.execute(sql).fetchone()


    @functools.lru_cache
    def view_make_select(self, name):
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                sql = first(cursor, TABLE_OR_VIEW_SQL, dict(name=name),
                            Class=str)
                return select_from_create_view(sql)
