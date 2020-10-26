#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib

import apsw
import Sql
from Const import (
    APPNAME, MAINWINDOWGEOMETRY, MAINWINDOWSTATE, OPENED, RECENT_FILES_MAX,
    RECENTFILE, WIN)


def path():
    return _the.config.path


def filename():
    return _the.config.filename


def get(key):
    return _the.config[key]


def set(key, value):
    _the.config[key] = value


def initialize(path):
    _the(path)


def _the(path):
    if _the.config is None:
        _the.config = _Singleton_Config(path)
_the.config = None # noqa


class _Singleton_Config:

    def __init__(self, path):
        self._path = path
        self._set_filename()


    @property
    def path(self):
        return self._path


    @property
    def filename(self):
        return self._filename


    def _set_filename(self):
        name = APPNAME.lower() + '.sbc'
        if WIN:
            names = [pathlib.Path.home() / name, self.path / name]
            index = 0
        else:
            names = [pathlib.Path.home() / '.config' / name,
                     pathlib.Path.home() / f'.{name}', self.path / name]
            index = 0 if (pathlib.Path.home() / '.config').is_dir() else 1
        for name in names:
            if name.exists():
                self._filename = str(name.resolve())
                self._update_opened()
                return
        self._filename = str(names[index].resolve())
        self._make_default_sbc()


    def _make_default_sbc(self):
        db = None
        try:
            db = apsw.Connection(self._filename)
            cursor = db.cursor()
            cursor.execute(_PREPARE)
            with Sql.Transaction(db) as cursor:
                cursor.execute(_CREATE)
                for n in range(1, RECENT_FILES_MAX + 1):
                    key = f'{RECENTFILE}/{n}'
                    cursor.execute(_INSERT_RECENT, dict(key=key))
        finally:
            if db is not None:
                db.close()


    def _update_opened(self):
        db = None
        try:
            db = apsw.Connection(self._filename)
            cursor = db.cursor()
            cursor.execute(_INCREMENT, dict(key=OPENED))
        finally:
            if db is not None:
                db.close()


    def __getitem__(self, key):
        db = None
        try:
            db = apsw.Connection(self._filename)
            Class = int
            if key in {MAINWINDOWGEOMETRY, MAINWINDOWSTATE}:
                Class = bytes
            return Sql.first(db.cursor(), _GET, dict(key=key), Class=Class)
        finally:
            if db is not None:
                db.close()


    def __setitem__(self, key, value):
        db = None
        try:
            db = apsw.Connection(self._filename)
            cursor = db.cursor()
            cursor.execute(_SET, dict(key=key, value=value))
        finally:
            if db is not None:
                db.close()


_PREPARE = '''
PRAGMA encoding = 'UTF-8';
PRAGMA foreign_keys = TRUE;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
DROP TABLE IF EXISTS config;
'''


_CREATE = f'''
CREATE TABLE config (
    key TEXT PRIMARY KEY NOT NULL,
    value BLOB
) WITHOUT ROWID;

INSERT INTO config (key, value) VALUES ('{OPENED}', 1);
INSERT INTO config (key, value) VALUES ('{MAINWINDOWSTATE}', NULL);
INSERT INTO config (key, value) VALUES ('{MAINWINDOWGEOMETRY}', NULL);
'''

_INSERT_RECENT = 'INSERT INTO config (key, value) VALUES (:key, NULL);'


_INCREMENT = 'UPDATE config SET value = value + 1 WHERE key = :key;'


_GET = 'SELECT value FROM config WHERE key = :key;'


_SET = 'UPDATE config SET value = :value WHERE key = :key;'
