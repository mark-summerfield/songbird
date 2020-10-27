#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib

import apsw
import Sql
from Const import (
    APPNAME, BLINK, LAST_FILE, MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE,
    OPENED, RECENT_FILE, RECENT_FILES_MAX, WIN)


class MainWindowOptions:

    def __init__(self, state=None, geometry=None, last_filename=None,
                 recent_files=None):
        self.state = state
        self.geometry = geometry
        self.last_filename = last_filename
        self.recent_files = recent_files if recent_files is not None else []


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


def write_main_window_options(options):
    _the.config.write_main_window_options(options)


def read_main_window_options():
    return _the.config.read_main_window_options()


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


    def _open(self):
        db = apsw.Connection(self._filename)
        cursor = db.cursor()
        cursor.execute(_PREPARE)
        version = Sql.first(cursor, _GET_VERSION)
        if version is None or version < _VERSION:
            self._update_sbc(cursor)
        return db, cursor


    def _update_sbc(self, cursor):
        cursor.execute(_UPDATE_VERSION)


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
            db, _ = self._open()
            with Sql.Transaction(db) as cursor:
                cursor.execute(_CREATE)
                for n in range(1, RECENT_FILES_MAX + 1):
                    key = f'{RECENT_FILE}/{n}'
                    cursor.execute(_INSERT_RECENT, dict(key=key))
        finally:
            if db is not None:
                db.close()


    def _update_opened(self):
        db = None
        try:
            db, cursor = self._open()
            cursor.execute(_INCREMENT, dict(key=OPENED))
        finally:
            if db is not None:
                db.close()


    def __getitem__(self, key):
        db = None
        try:
            db, cursor = self._open()
            Class = int
            if key in {MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE}:
                Class = bytes
            elif key == BLINK:
                Class = bool
            return Sql.first(cursor, _GET, dict(key=key), Class=Class)
        finally:
            if db is not None:
                db.close()


    def __setitem__(self, key, value):
        db = None
        try:
            db, cursor = self._open()
            cursor.execute(_SET, dict(key=key, value=value))
        finally:
            if db is not None:
                db.close()


    def write_main_window_options(self, options):
        db = None
        try:
            db, _ = self._open()
            with Sql.Transaction(db) as cursor:
                cursor.execute(_SET, dict(key=MAIN_WINDOW_STATE,
                                          value=options.state))
                cursor.execute(_SET, dict(key=MAIN_WINDOW_GEOMETRY,
                                          value=options.geometry))
                cursor.execute(_SET, dict(key=LAST_FILE,
                                          value=options.last_filename))
                cursor.execute(_CLEAR_RECENT_FILES)
                for n, name in enumerate(options.recent_files, 1):
                    if name and pathlib.Path(name).exists():
                        cursor.execute(_SET, dict(key=f'{RECENT_FILE}/{n}',
                                                  value=str(name)))
        finally:
            if db is not None:
                db.close()


    def read_main_window_options(self):
        options = MainWindowOptions()
        db = None
        try:
            db, _ = self._open()
            with Sql.Transaction(db) as cursor:
                options.state = Sql.first(
                    cursor, _GET, dict(key=MAIN_WINDOW_STATE), Class=bytes)
                options.geometry = Sql.first(
                    cursor, _GET, dict(key=MAIN_WINDOW_GEOMETRY),
                    Class=bytes)
                options.last_filename = Sql.first(
                    cursor, _GET, dict(key=LAST_FILE), Class=str)
                for n in range(1, RECENT_FILES_MAX + 1):
                    name = Sql.first(cursor, _GET,
                                     dict(key=f'{RECENT_FILE}/{n}'),
                                     Class=str)
                    if name:
                        name = pathlib.Path(name)
                        if name.exists():
                            options.recent_files.append(str(name.resolve()))
                return options
        finally:
            if db is not None:
                db.close()


_VERSION = 1


_PREPARE = f'''
PRAGMA encoding = 'UTF-8';
PRAGMA foreign_keys = TRUE;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
'''


_CREATE = f'''
PRAGMA user_version = {_VERSION};

DROP TABLE IF EXISTS config;

CREATE TABLE config (
    key TEXT PRIMARY KEY NOT NULL,
    value BLOB
) WITHOUT ROWID;

INSERT INTO config (key, value) VALUES ('{OPENED}', 1);
INSERT INTO config (key, value) VALUES ('{MAIN_WINDOW_STATE}', NULL);
INSERT INTO config (key, value) VALUES ('{MAIN_WINDOW_GEOMETRY}', NULL);
INSERT INTO config (key, value) VALUES ('{LAST_FILE}', NULL);
INSERT INTO config (key, value) VALUES ('{BLINK}', TRUE);
'''

_INSERT_RECENT = 'INSERT INTO config (key, value) VALUES (:key, NULL);'


_INCREMENT = 'UPDATE config SET value = value + 1 WHERE key = :key;'


_GET = 'SELECT value FROM config WHERE key = :key;'


_SET = 'UPDATE config SET value = :value WHERE key = :key;'


_CLEAR_RECENT_FILES = f'''
UPDATE config SET value = NULL WHERE key LIKE '{RECENT_FILE}%';'''


_GET_VERSION = 'PRAGMA user_version;'


_UPDATE_VERSION = f'PRAGMA user_version = {_VERSION};'
