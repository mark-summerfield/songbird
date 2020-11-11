#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import collections
import pathlib

import apsw
from Const import (
    APPNAME, LAST_FILE, MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE, OPENED,
    RECENT_FILE, RECENT_FILES_MAX, SHOW_AS_TABS, SHOW_CONTENTS,
    SHOW_PRAGMAS, WIN)
from Sql import first


class MainWindowOptions:

    def __init__(self, *, state=None, geometry=None, last_filename=None,
                 recent_files=None, show_contents=True, show_pragmas=False,
                 show_as_tabs=False):
        self.state = state
        self.geometry = geometry
        self.last_filename = last_filename
        self.recent_files = recent_files if recent_files is not None else []
        self.show_contents = show_contents
        self.show_pragmas = show_pragmas
        self.show_as_tabs = show_as_tabs


ToggleOptions = collections.namedtuple(
    'ToggleOptions', ('show_contents', 'show_pragmas', 'show_tabs'))


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
        version = first(cursor, _GET_VERSION)
        if version is None or version < _VERSION:
            self._update_sbc(db, cursor)
        return db, cursor


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
            db = apsw.Connection(self._filename) # Mustn't call _open here
            cursor = db.cursor()
            cursor.execute(_PREPARE)
            with db:
                cursor.execute(_CREATE)
                for n in range(1, RECENT_FILES_MAX + 1):
                    key = f'{RECENT_FILE}/{n}'
                    cursor.execute(_INSERT_RECENT, dict(key=key))
        finally:
            if db is not None:
                db.close()


    def _update_opened(self):
        d = dict(key=OPENED)
        vacuum = False
        db = None
        try:
            db, cursor = self._open()
            with db:
                cursor.execute(_INCREMENT, d)
                if first(cursor, _GET, d) > 100:
                    d.update(value=1)
                    cursor.execute(_SET, d)
                    vacuum = True
            if vacuum:
                cursor.execute('VACUUM;')
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
            return first(cursor, _GET, dict(key=key), Class=Class)
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
            db, cursor = self._open()
            with db:
                cursor.execute(_SET, dict(key=MAIN_WINDOW_STATE,
                                          value=options.state))
                cursor.execute(_SET, dict(key=MAIN_WINDOW_GEOMETRY,
                                          value=options.geometry))
                cursor.execute(_SET, dict(key=LAST_FILE,
                                          value=options.last_filename))
                cursor.execute(_SET, dict(key=SHOW_CONTENTS,
                                          value=options.show_contents))
                cursor.execute(_SET, dict(key=SHOW_PRAGMAS,
                                          value=options.show_pragmas))
                cursor.execute(_SET, dict(key=SHOW_AS_TABS,
                                          value=options.show_as_tabs))
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
            db, cursor = self._open()
            with db:
                options.state = first(
                    cursor, _GET, dict(key=MAIN_WINDOW_STATE), Class=bytes)
                options.geometry = first(
                    cursor, _GET, dict(key=MAIN_WINDOW_GEOMETRY),
                    Class=bytes)
                options.last_filename = first(
                    cursor, _GET, dict(key=LAST_FILE), Class=str)
                options.show_contents = first(
                    cursor, _GET, dict(key=SHOW_CONTENTS), Class=bool)
                options.show_pragmas = first(
                    cursor, _GET, dict(key=SHOW_PRAGMAS), Class=bool)
                options.show_as_tabs = first(
                    cursor, _GET, dict(key=SHOW_AS_TABS), Class=bool)
                for n in range(1, RECENT_FILES_MAX + 1):
                    if name := first(
                            cursor, _GET, dict(key=f'{RECENT_FILE}/{n}'),
                            Class=str):
                        name = pathlib.Path(name)
                        if name.exists():
                            options.recent_files.append(str(name.resolve()))
                return options
        finally:
            if db is not None:
                db.close()


    def _update_sbc(self, db, cursor):
        cursor.execute(_UPDATE_VERSION)
        with db:
            # 3
            cursor.execute(f'''
                INSERT INTO config (key, value)
                SELECT '{SHOW_CONTENTS}', TRUE
                WHERE NOT EXISTS (SELECT 1 FROM config
                                  WHERE key = '{SHOW_CONTENTS}');''')
            # 4
            cursor.execute(f'''
                INSERT INTO config (key, value)
                SELECT '{SHOW_PRAGMAS}', FALSE
                WHERE NOT EXISTS (SELECT 1 FROM config
                                  WHERE key = '{SHOW_PRAGMAS}');''')
            # 5
            cursor.execute('''DELETE FROM config WHERE key = 'Blink';''')
            # 6
            cursor.execute(f''' 
                INSERT INTO config (key, value)
                SELECT '{SHOW_AS_TABS}', FALSE
                WHERE NOT EXISTS (SELECT 1 FROM config
                                  WHERE key = '{SHOW_AS_TABS}');''')
            # 7
            # CREATE TABLE IF NOT EXISTS FILES (...
            # CREATE TABLE IF NOT EXISTS WINDOWS (...


_VERSION = 6


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
INSERT INTO config (key, value) VALUES ('{SHOW_CONTENTS}', TRUE);
INSERT INTO config (key, value) VALUES ('{SHOW_PRAGMAS}', FALSE);
INSERT INTO config (key, value) VALUES ('{SHOW_AS_TABS}', FALSE);

-- TODO
/*
CREATE TABLE files (
    fid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    filename TEXT,
    updated INTEGER DEFAULT STRFTIME('%s', 'NOW'),
    -- etc.
);

CREATE TABLE windows (
    -- etc.
);
*/
'''

_INSERT_RECENT = 'INSERT INTO config (key, value) VALUES (:key, NULL);'

_INCREMENT = 'UPDATE config SET value = value + 1 WHERE key = :key;'

_GET = 'SELECT value FROM config WHERE key = :key;'

_SET = 'UPDATE config SET value = :value WHERE key = :key;'

_CLEAR_RECENT_FILES = f'''
UPDATE config SET value = NULL WHERE key LIKE '{RECENT_FILE}%';'''

_GET_VERSION = 'PRAGMA user_version;'

_UPDATE_VERSION = f'PRAGMA user_version = {_VERSION};'
