#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import collections
import pathlib

from PySide2.QtCore import QStandardPaths

import apsw
from Const import (
    APPNAME, LAST_FILE, MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE, OPENED,
    RECENT_FILE, RECENT_FILES_MAX, SHOW_AS_TABS, SHOW_ITEMS_TREE,
    SHOW_PRAGMAS, WIN)
from Db.Sql import first

from .Const import (
    _CLEAR_RECENT_FILES, _CREATE, _GET, _GET_VERSION, _INCREMENT,
    _INSERT_RECENT, _PREPARE, _SET, _UPDATE_VERSION, _VERSION)


class MainWindowOptions:

    def __init__(self, *, state=None, geometry=None, last_filename=None,
                 recent_files=None, show_items_tree=True,
                 show_pragmas=False, show_as_tabs=False):
        self.state = state
        self.geometry = geometry
        self.last_filename = last_filename
        self.recent_files = recent_files if recent_files is not None else []
        self.show_items_tree = show_items_tree
        self.show_pragmas = show_pragmas
        self.show_as_tabs = show_as_tabs


ToggleOptions = collections.namedtuple(
    'ToggleOptions', ('show_items_tree', 'show_pragmas', 'show_tabs'))


def filename():
    return _Config.filename


def get(key):
    return _Config[key]


def set(key, value):
    _Config[key] = value


def write_main_window_options(options):
    _Config.write_main_window_options(options)


def read_main_window_options():
    return _Config.read_main_window_options()


class _Singleton_Config:

    def __init__(self):
        self._set_filename()


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
        path = QStandardPaths.writableLocation(
            QStandardPaths.AppConfigLocation)
        if path:
            path = pathlib.Path(path) / name
        elif WIN:
            path = pathlib.Path.home() / name
        else:
            path = pathlib.Path.home() / '.config'
            if path.exists():
                path /= name
            else:
                path = pathlib.Path.home() / f'.{name}'
        self._filename = str(path.resolve())
        if path.exists():
            self._update_opened()
        else:
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
                cursor.execute(_SET, dict(key=SHOW_ITEMS_TREE,
                                          value=options.show_items_tree))
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
                options.show_items_tree = first(
                    cursor, _GET, dict(key=SHOW_ITEMS_TREE), Class=bool)
                options.show_pragmas = first(
                    cursor, _GET, dict(key=SHOW_PRAGMAS), Class=bool)
                options.show_as_tabs = first(
                    cursor, _GET, dict(key=SHOW_AS_TABS), Class=bool)
                for n in range(1, RECENT_FILES_MAX + 1):
                    if name := first(cursor,
                                     _GET, dict(key=f'{RECENT_FILE}/{n}'),
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
            cursor.execute(f'''
                DELETE FROM config WHERE key = 'ShowContents';
                INSERT INTO config (key, value)
                SELECT '{SHOW_ITEMS_TREE}', TRUE
                WHERE NOT EXISTS (SELECT 1 FROM config
                                  WHERE key = '{SHOW_ITEMS_TREE}');''')
            # 8 TODO
            # CREATE TABLE IF NOT EXISTS FILES (...
            # CREATE TABLE IF NOT EXISTS WINDOWS (...


_Config = _Singleton_Config()
