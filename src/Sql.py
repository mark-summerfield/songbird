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


@functools.lru_cache
def quoted(name, *, quote='"', force=False):
    name = name.strip('\'"')
    return (f'{quote}{name}{quote}' if force or
            not re.fullmatch(r'\w+', name) else name)


@functools.lru_cache
def uncommented(sql):
    # Simple-minded, e.g., incorrect if -- or /* is inside a string etc.
    return re.sub(r'/\*.*?\*/', '', re.sub(r'--.*', '', sql),
                  flags=re.DOTALL).lstrip()


@functools.lru_cache
def select_limit_1_from_select(select, row=0):
    limit_rx = re.compile(
        r'\sLIMIT\s+\d+(:?\s+OFFSET\s+(?P<offset>\d+))?', re.IGNORECASE)
    if match := limit_rx.search(select):
        if offset := match.group('offset'):
            row += int(offset)
        select = limit_rx.sub(' LIMIT 1', select)
    else: # No original limit set
        select = select.rstrip(';') + ' LIMIT 1'
    return select + f' OFFSET {row}'


def select_from_create_view(sql):
    if match := re.search(r'CREATE\s+VIEW.+?\s+AS\s+(?P<sql>.+)\s*;?', sql,
                          re.IGNORECASE | re.DOTALL):
        return match.group('sql')


def field_count_from_select(select):
    return field_names_from_select(select, count=True)


@functools.lru_cache
def field_names_from_select(select, *, count=False):
    select = uncommented(select)
    as_rx = re.compile(r'\s*(:?.*)\s+[Aa][Ss]\s+(?P<alias>.*)\s*')
    results = []
    if match := re.search(r'SELECT(?:\s+(:?ALL|DISTINCT))?\s+'
                          r'(?P<fields>.*?)\s+from', select,
                          re.IGNORECASE | re.DOTALL):
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
        if count:
            return len(fields)
        for field in fields:
            alias = None
            if match := as_rx.match(field):
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
    def check_fields_from_select(n, sql, expected=None):
        actual = field_names_from_select(sql)
        if actual != expected:
            sql = ' '.join(sql.split())
            print(f'{n} SQL: {sql}\n  Exp: {expected}\n  Act: {actual}')
            return 1
        return 0

    n = errors = 0
    n += 1
    sql = 'select distinct kid, name as "Kiosk Name" from kiosks'
    errors += check_fields_from_select(n, sql, ('kid', 'Kiosk Name')) # 1
    n += 1
    sql = 'select id from stations'
    errors += check_fields_from_select(n, sql, ('id',)) # 2
    sql = '''
SELECT stations.id AS 'Station ID', stations.name as Station,
stations.zone, kiosks.name as "Kiosk Name"
FROM stations, kiosks WHERE stations.id = kiosks.sid;'''
    n += 1
    errors += check_fields_from_select( # 3
        n, sql, ('Station ID', 'Station', 'stations.zone', 'Kiosk Name'))
    sql = '''
SELECT f(a), g(b, h(c, d)), x + y, e, t1.h, t2.i,
f(a) as fa, g(b, h(c, d)) as gbh, x + y as xy, e as E,
t1.h as "T H #1", t2.i as 'T 2 I' FROM t1, t2 WHERE t1.id = t2.id
ORDER BY t2.name DESC;'''
    n += 1
    errors += check_fields_from_select( # 4
        n, sql, ('f(a)', 'g(b, h(c, d))', 'x + y', 'e', 't1.h', 't2.i',
                 'fa', 'gbh', 'xy', 'E', 'T H #1', 'T 2 I'))
    n += 1
    errors += check_fields_from_select( # 5
        n, 'SELECT COUNT(*) FROM Stations WHERE zone >= 1.5;',
        ('COUNT(*)',))
    n += 1
    try:
        check_fields_from_select(n, 'SELECT * FROM Kiosks;') # 6
        errors += 1 # unexpected
    except Error:
        pass # expected
    n += 1
    try:
        check_fields_from_select(n, 'SELECT FROM stations;') # 7
        errors += 1 # unexpected
    except Error:
        pass # expected
    if errors:
        print(f'{n - errors:,}/{n:,} passed, {errors:,}/{n:,} failed')
    else:
        print(f'All {n:,} OK')
