#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import apsw
from Sql import (
    CONTENT_DETAIL, CONTENT_SUMMARY, ContentDetail, ContentSummary, Pragmas,
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
