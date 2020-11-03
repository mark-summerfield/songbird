#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import collections
import functools
import re

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


def select_from_create_view(sql):
    sql_rx = re.compile(r'create\s+view.+?\s+as\s+(?P<sql>.+)\s*;?',
                        re.IGNORECASE | re.DOTALL)
    match = sql_rx.search(sql)
    if match is not None:
        return match.group('sql')


@functools.lru_cache
def fields_from_select(select):
    # TODO FIXME
    import re
    rx = re.compile(r'select\s+(?P<fields>.*?)\s+from',
                    re.IGNORECASE | re.DOTALL)
    match = rx.search(select)
    if match is not None:
        return [name.strip() for name in match.group('fields').split(',')]


CONTENT_SUMMARY = '''
SELECT type, name FROM sqlite_master ORDER BY UPPER(name);'''

ContentSummary = collections.namedtuple('ContentSummary', ('kind', 'name'))

CONTENT_DETAIL = 'SELECT * FROM pragma_table_info(:name);'

ContentDetail = collections.namedtuple(
    'ContentDetail', ('name', 'type', 'notnull', 'default', 'pk'))

TABLE_OR_VIEW_SQL = 'SELECT sql FROM sqlite_master WHERE name = :name'


class Pragmas:

    def __init__(self, *, user_version=0):
        self.user_version = user_version


    @staticmethod
    def unchanged():
        return Pragmas(user_version=UNCHANGED)


if __name__ == '__main__':
    ok = True
    sql = '''
SELECT stations.id AS "Station ID", stations.name as Station,
stations.zone, kiosks.name as "Kiosk Name"
FROM stations, kiosks WHERE stations.id = kiosks.sid;'''
    actual = fields_from_select(sql)
    expected = ('Station ID', 'Station', 'zone', 'Kiosk Name')
    if actual != expected:
        sql = ' '.join(sql.split())
        print(f'SQL: {sql}\n  Exp: {expected}\n  Act: {actual}')
        ok = False
    sql = '''
SELECT f(a), g(b, h(c, d)), x + y, e, t1.h, t2.i,
f(a) as fa, g(b, h(c, d)) as gbh, x + y as xy, e as E,
t1.h as t1h, t2.i as t2i FROM t1, t2 WHERE t1.id = t2.id
ORDER BY t2.name DESC;'''
    actual = fields_from_select(sql)
    expected = ('f(a)', 'g(b, h(c, d))', 'x + y', 'e', 't1.h', 't2.i',
                'fa', 'gbh', 'xy', 'E', 't1h', 't2i')
    if actual != expected:
        sql = ' '.join(sql.split())
        print(f'SQL: {sql}\n  Exp: {expected}\n  Act: {actual}')
        ok = False
    print('OK' if ok else 'Failed')
