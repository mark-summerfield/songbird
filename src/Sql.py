#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.


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
