#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import json
import pathlib

from PySide2.QtCore import QStandardPaths

import apsw
from Const import (
    APPNAME, LAST_FILE, MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE, OPENED,
    RECENT_FILE, RECENT_FILES_MAX, SHOW_AS_TABS, SHOW_ITEMS_TREE,
    SHOW_PRAGMAS, WIN)
from Db.Sql import first

from .Const import (
    _CLEAR_FILE_UI, _CLEAR_RECENT_FILES, _CREATE, _DELETE_OLD, _GET,
    _GET_FILE_UI, _GET_VERSION, _GET_WINDOW_UI, _INCREMENT, _INSERT_FILE_UI,
    _INSERT_RECENT, _INSERT_WINDOW_UI, _PREPARE, _SET, _UPDATE_VERSION,
    _VERSION)
from .Struct import DbUi, DbWindowUi, MainWindowOptions


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
        filename = str(pathlib.Path(ui.filename).resolve())
        db = None
        try:
            db, cursor = self._open()
            with db:
                cursor.execute(_CLEAR_FILE_UI, dict(filename=filename))
                cursor.execute(_INSERT_FILE_UI, dict(filename=filename,
                                                     ui=ui.to_json))
                fid = db.last_insert_rowid()
                for window in ui.windows:
                    cursor.execute(_INSERT_WINDOW_UI,
                                   dict(fid=fid, ui=window.to_json))
        finally:
            if db is not None:
                db.close()


    def read_db_ui(self, filename):
        filename = str(pathlib.Path(filename).resolve())
        ui = DbUi(filename)
        db = None
        try:
            db, cursor = self._open()
            with db:
                row = cursor.execute(_GET_FILE_UI,
                                     dict(filename=filename)).fetchone()
                if row is not None:
                    fid = int(row[0])
                    ui.update(json.loads(row[1]))
                    for row in cursor.execute(_GET_WINDOW_UI,
                                              dict(fid=fid)):
                        d = json.loads(row[0])
                        if d.get('title') and d.get('sql_select'):
                            ui.windows.append(DbWindowUi(**d))
        finally:
            if db is not None:
                db.close()
        return ui


    def _update_sbc(self, db, cursor):
        cursor.execute(_UPDATE_VERSION)
        with db:
            # _VERSION = 13
            cursor.execute(f'''
                DROP TRIGGER IF EXISTS files_on_update;
                DROP TABLE IF EXISTS windows;
                DROP TABLE IF EXISTS files;
                CREATE TABLE files (
                    fid INTEGER PRIMARY KEY NOT NULL,
                    filename TEXT NOT NULL,
                    updated INTEGER DEFAULT (STRFTIME('%s', 'NOW'))
                            NOT NULL,
                    ui TEXT
                );
                CREATE TRIGGER files_on_update AFTER UPDATE ON files
                    FOR EACH ROW BEGIN
                        UPDATE files SET updated = STRFTIME('%s', 'NOW')
                        WHERE fid = OLD.fid;
                    END;
                CREATE TABLE windows (
                    wid INTEGER PRIMARY KEY NOT NULL,
                    fid INTEGER NOT NULL,
                    ui TEXT,
                    UNIQUE(wid, fid),
                    FOREIGN KEY(fid) REFERENCES files(fid) ON DELETE CASCADE
                );''')


_Config = _Singleton_Config()
