#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import collections
import functools
import re

from Const import UNCHANGED


class Error(Exception):
    pass


class Pragmas:

    def __init__(self, *, user_version=0):
        self.user_version = user_version


    @staticmethod
    def unchanged():
        return Pragmas(user_version=UNCHANGED)


def first(cursor, sql, d=None, *, default=None, Class=int):
    d = {} if d is None else d
    record = cursor.execute(sql, d).fetchone()
    if record is None:
        return default # Deliberately ignores Class
    value = record[0]
    if value is None:
        return value
    return bool(int(value)) if isinstance(Class, bool) else Class(value)


def select_from_create_view(sql):
    match = re.search(r'create\s+view.+?\s+as\s+(?P<sql>.+)\s*;?', sql,
                      re.IGNORECASE | re.DOTALL)
    if match is not None:
        return match.group('sql')


@functools.lru_cache
def fields_from_select(select):
    as_rx = re.compile(r'\s*(:?.*)\s+[Aa][Ss]\s+(?P<alias>.*)\s*')
    results = []
    match = re.search(r'select\s+(?P<fields>.*?)\s+from', select,
                      re.IGNORECASE | re.DOTALL)
    if match is not None:
        fields = match.group('fields')
        if fields == '*':
            raise Error('Cannot determine field names from SELECT *')
        if '(' not in fields:
            fields = fields.split(',')
        else:
            parts = []
            parens = 0
            for c in fields:
                if c == ',' and parens:
                    parts.append('\f')
                    continue
                if c == '(':
                    parens += 1
                elif c == ')':
                    parens -= 1
                parts.append(c)
            parts = ''.join(parts)
            fields = [part.replace('\f', ',') for part in parts.split(',')]
        for field in fields:
            alias = None
            match = as_rx.match(field)
            if match is None:
                i = field.rfind('.')
                if i > -1:
                    i += 1
                    if len(field[i:]):
                        field = field[i:]
            else:
                alias = match.group('alias')
            results.append((alias or field).strip().strip('\'"'))
        return tuple(results)
    raise Error('Failed to determine field names')


CONTENT_SUMMARY = '''
SELECT type, name FROM sqlite_master ORDER BY UPPER(name);'''

ContentSummary = collections.namedtuple('ContentSummary', ('kind', 'name'))

CONTENT_DETAIL = 'SELECT * FROM pragma_table_info(:name);'

ContentDetail = collections.namedtuple(
    'ContentDetail', ('name', 'type', 'notnull', 'default', 'pk'))

TABLE_OR_VIEW_SQL = 'SELECT sql FROM sqlite_master WHERE name = :name'


if __name__ == '__main__':
    def check_fields_from_select(sql, expected=None):
        actual = fields_from_select(sql)
        if actual != expected:
            sql = ' '.join(sql.split())
            print(f'SQL: {sql}\n  Exp: {expected}\n  Act: {actual}')
            return 1
        return 0

    tests = errors = 0
    sql = '''
SELECT stations.id AS 'Station ID', stations.name as Station,
stations.zone, kiosks.name as "Kiosk Name"
FROM stations, kiosks WHERE stations.id = kiosks.sid;'''
    tests += 1
    errors += check_fields_from_select(
        sql, ('Station ID', 'Station', 'zone', 'Kiosk Name'))
    sql = '''
SELECT f(a), g(b, h(c, d)), x + y, e, t1.h, t2.i,
f(a) as fa, g(b, h(c, d)) as gbh, x + y as xy, e as E,
t1.h as "T H #1", t2.i as 'T 2 I' FROM t1, t2 WHERE t1.id = t2.id
ORDER BY t2.name DESC;'''
    tests += 1
    errors += check_fields_from_select(
        sql, ('f(a)', 'g(b, h(c, d))', 'x + y', 'e', 'h', 'i', 'fa', 'gbh',
              'xy', 'E', 'T H #1', 'T 2 I'))
    tests += 1
    errors += check_fields_from_select(
        'SELECT COUNT(*) FROM Stations WHERE zone >= 1.5;', ('COUNT(*)',))
    tests += 1
    try:
        check_fields_from_select('SELECT * FROM Kiosks;')
        errors += 1 # unexpected
    except Error:
        pass # expected
    tests += 1
    try:
        check_fields_from_select('SELECT FROM stations;')
        errors += 1 # unexpected
    except Error:
        pass # expected
    if errors:
        print(f'{tests - errors:,}/{tests:,} passed, '
              f'{errors:,}/{tests:,} failed')
    else:
        print(f'All {tests:,} OK')
