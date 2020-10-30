#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import collections

from Const import UNCHANGED


def first(cursor, sql, d=None, *, default=None, Class=int):
    d = {} if d is None else d
    record = cursor.execute(sql, d).fetchone()
    if record is None:
        return default # Deliberately ignores Class
    value = record[0]
    if value is None:
        return value
    return bool(int(value)) if isinstance(Class, bool) else Class(value)


CONTENT_SUMMARY = '''
SELECT type, name FROM sqlite_master ORDER BY UPPER(name);'''

ContentSummary = collections.namedtuple('ContentSummary', ('kind', 'name'))

CONTENT_DETAIL = 'SELECT * FROM pragma_table_info(:name);'

ContentDetail = collections.namedtuple(
    'ContentDetail', ('name', 'type', 'notnull', 'pk'))


class Pragmas:

    def __init__(self, *, user_version=0):
        self.user_version = user_version


    @staticmethod
    def unchanged():
        return Pragmas(user_version=UNCHANGED)
