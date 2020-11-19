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
    _CLEAR_RECENT_FILES, _CREATE, _DELETE_OLD, _GET, _GET_VERSION,
    _INCREMENT, _INSERT_RECENT, _PREPARE, _SET, _UPDATE_VERSION, _VERSION)


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


class DbUi:

    def __init__(self, filename, mdi=True, show_items_tree=True,
                 show_pragmas=False, show_calendar=False, windows=None):
        self.filename = filename
        self.mdi = mdi
        self.show_items_tree = show_items_tree
        self.show_pragmas = show_pragmas
        self.show_calendar = show_calendar
        self.windows = windows


class DbWindowUi:

    def __init__(self, title, sql_select, x=None, y=None, width=None,
                 height=None, tab_pos=None, editor_height=None):
        self.title = title
        self.sql_select = sql_select
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tab_pos = tab_pos
        self.editor_height = editor_height


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


def write_db_ui(ui):
    _Config.write_db_ui(ui)


def read_db_ui(filename):
    return _Config.read_db_ui(filename)


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
            self._update_on_open()
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


    def _update_on_open(self):
        d = dict(key=OPENED)
        vacuum = False
        db = None
        try:
            db, cursor = self._open()
            with db:
                cursor.execute(_DELETE_OLD)
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


    def write_db_ui(self, ui):
        # TODO save to .sbc
        print('write_db_ui', vars(ui))


    def read_db_ui(self, filename): # TODO
        ui = DbUi(filename)
        # TODO populate from .sbc if poss
        print('read_db_ui', filename)
        return ui


    def _update_sbc(self, db, cursor):
        cursor.execute(_UPDATE_VERSION)
        with db:
            # _VERSION = 4
            cursor.execute(f'''
                INSERT INTO config (key, value)
                SELECT '{SHOW_PRAGMAS}', FALSE
                WHERE NOT EXISTS (SELECT 1 FROM config
                                  WHERE key = '{SHOW_PRAGMAS}');''')
            # _VERSION = 5
            cursor.execute('''DELETE FROM config WHERE key = 'Blink';''')
            # _VERSION = 6
            cursor.execute(f''' 
                INSERT INTO config (key, value)
                SELECT '{SHOW_AS_TABS}', FALSE
                WHERE NOT EXISTS (SELECT 1 FROM config
                                  WHERE key = '{SHOW_AS_TABS}');''')
            # _VERSION = 7
            cursor.execute(f'''
                DELETE FROM config WHERE key = 'ShowContents';
                INSERT INTO config (key, value)
                SELECT '{SHOW_ITEMS_TREE}', TRUE
                WHERE NOT EXISTS (SELECT 1 FROM config
                                  WHERE key = '{SHOW_ITEMS_TREE}');''')
            # _VERSION = 8
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS files (
                    fid INTEGER PRIMARY KEY NOT NULL,
                    filename TEXT NOT NULL,
                    updated INTEGER DEFAULT (STRFTIME('%s', 'NOW')) NOT NULL,
                    mdi INTEGER DEFAULT TRUE NOT NULL,
                    show_items_tree INTEGER DEFAULT TRUE NOT NULL,
                    show_pragmas INTEGER DEFAULT FALSE NOT NULL,
                    show_calendar INTEGER DEFAULT FALSE NOT NULL,
                    CHECK(mdi IN (0, 1)),
                    CHECK(show_items_tree IN (0, 1)),
                    CHECK(show_pragmas IN (0, 1)),
                    CHECK(show_calendar IN (0, 1))
                );
                CREATE TABLE IF NOT EXISTS windows (
                    wid INTEGER PRIMARY KEY NOT NULL,
                    fid INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    sql_select TEXT NOT NULL,
                    x INTEGER,
                    y INTEGER,
                    width INTEGER,
                    height INTEGER,
                    tab_pos INTEGER,
                    editor_height INTEGER,
                    CHECK(x IS NULL OR x >= 0),
                    CHECK(y IS NULL OR y >= 0),
                    CHECK(width IS NULL OR width > 0),
                    CHECK(height IS NULL OR height > 0),
                    CHECK(tab_pos IS NULL OR tab_pos >= 0),
                    CHECK(editor_height IS NULL OR editor_height >= 0),
                    UNIQUE(wid, fid),
                    FOREIGN KEY(fid) REFERENCES files(fid) ON DELETE CASCADE
                );''')
            # _VERSION = 10
            cursor.execute(f'''
                CREATE TRIGGER IF NOT EXISTS files_on_update
                    AFTER UPDATE ON files
                    FOR EACH ROW BEGIN
                        UPDATE files SET updated = STRFTIME('%s', 'NOW')
                        WHERE fid = OLD.fid;
                    END;''')


_Config = _Singleton_Config()
