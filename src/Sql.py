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


class Transaction:

    def __init__(self, db):
        self.db = db


    def __enter__(self):
        self.cursor = self.db.cursor()
        self.cursor.execute("BEGIN;")
        return self.cursor


    def __exit__(self, exc_type, _exc_val, _exc_tb):
        if exc_type is None:
            self.cursor.execute("COMMIT;")
        else:
            self.cursor.execute("ROLLBACK;") # Exception will be raised
