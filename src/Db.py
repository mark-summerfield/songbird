#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import functools
import re

import apsw
import Sql
from Const import UNCHANGED


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


    @property
    def is_songbird(self):
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                return bool(Sql.first(cursor, Sql.IS_SONGBIRD, default=0))
        return False


    def content_summary(self):
        if self._db is not None:
            cursor = self._db.cursor()
            for row in cursor.execute(Sql.CONTENT_SUMMARY):
                content = Sql.ContentSummary(*row)
                if content.name.startswith(('sqlite_', 'songbird_')):
                    continue
                # TODO also skip FTS implementation tables
                yield content


    def content_detail(self, name):
        if self._db is not None:
            cursor = self._db.cursor()
            for row in cursor.execute(Sql.CONTENT_DETAIL, dict(name=name)):
                yield Sql.ContentDetail(*row[1:])


    def pragmas(self):
        pragmas = Sql.Pragmas()
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                pragmas.user_version = Sql.first(
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
        if self._db is not None:
            sql = f'SELECT COUNT(*) FROM ({Sql.uncommented(select)})'
            cursor = self._db.cursor()
            with self._db:
                return Sql.first(cursor, sql, default=0)
        return 0


    @functools.lru_cache
    def table_make_select(self, name):
        fields = []
        for detail in self.content_detail(name):
            fields.append(Sql.quoted(detail.name))
        fields = ', '.join(fields)
        return (f'SELECT {fields}\nFROM {Sql.quoted(name)}\n'
                '--WHERE \n--ORDER BY ')


    def table_row(self, select, row): # Rely on SQLite to cache
        if self._db is not None:
            select = Sql.select_limit_1_from_select(select, row)
            cursor = self._db.cursor()
            with self._db:
                return cursor.execute(select).fetchone()


    @functools.lru_cache
    def view_make_select(self, name):
        if self._db is not None:
            cursor = self._db.cursor()
            with self._db:
                sql = Sql.first(cursor, Sql.TABLE_OR_VIEW_SQL,
                                dict(name=name), Class=str)
                return re.sub(r'\s+(from|where|order\s+by)\s', r'\n\1 ',
                              Sql.select_from_create_view(sql),
                              flags=re.IGNORECASE | re.DOTALL)


    def field_names_for_select(self, select):
        # Usually try Sql.field_names_from_select() first
        if self._db is not None:
            select = Sql.select_limit_1_from_select(select)
            cursor = self._db.cursor()
            with self._db:
                try:
                    cursor.execute(select)
                    return [Sql.quoted(item[0])
                            for item in cursor.getdescription()]
                except (apsw.SQLError, apsw.ExecutionCompleteError):
                    return () # No matching rows
