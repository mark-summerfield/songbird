#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from Const import (
    LAST_FILE, MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE, OPENED, RECENT_FILE,
    SHOW_AS_TABS, SHOW_ITEMS_TREE, SHOW_PRAGMAS)

_VERSION = 13

_PREPARE = f'''
PRAGMA encoding = 'UTF-8';
PRAGMA foreign_keys = TRUE;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
'''

_CREATE = f'''
PRAGMA user_version = {_VERSION};

DROP TRIGGER IF EXISTS files_on_update;
DROP TABLE IF EXISTS windows;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS config;

CREATE TABLE config (
    key TEXT PRIMARY KEY NOT NULL,
    value BLOB
) WITHOUT ROWID;

INSERT INTO config (key, value) VALUES ('{OPENED}', 1);
INSERT INTO config (key, value) VALUES ('{MAIN_WINDOW_STATE}', NULL);
INSERT INTO config (key, value) VALUES ('{MAIN_WINDOW_GEOMETRY}', NULL);
INSERT INTO config (key, value) VALUES ('{LAST_FILE}', NULL);
INSERT INTO config (key, value) VALUES ('{SHOW_ITEMS_TREE}', TRUE);
INSERT INTO config (key, value) VALUES ('{SHOW_PRAGMAS}', FALSE);
INSERT INTO config (key, value) VALUES ('{SHOW_AS_TABS}', FALSE);

CREATE TABLE files (
    fid INTEGER PRIMARY KEY NOT NULL,
    filename TEXT NOT NULL,
    updated INTEGER DEFAULT (STRFTIME('%s', 'NOW')) NOT NULL,
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
);
'''
# Both tables above in effect AUTOINCREMENT because their PKs are ROWID
# aliases
# SQLite doesn't support compound PKs with one of them AUTOINCREMENT, so the
# workaround is to use UNIQUE

_INSERT_RECENT = 'INSERT INTO config (key, value) VALUES (:key, NULL);'

_INCREMENT = 'UPDATE config SET value = value + 1 WHERE key = :key;'

_GET = 'SELECT value FROM config WHERE key = :key;'

_SET = 'UPDATE config SET value = :value WHERE key = :key;'

_CLEAR_RECENT_FILES = f'''
UPDATE config SET value = NULL WHERE key LIKE '{RECENT_FILE}%';'''

_GET_VERSION = 'PRAGMA user_version;'

_UPDATE_VERSION = f'PRAGMA user_version = {_VERSION};'

_DELETE_OLD = '''
DELETE FROM files WHERE updated < STRFTIME('%s', 'NOW', '-1 YEAR');'''
# Delete record of opened databases that haven't been opened in more than a
# year: really ought to be a user-specified time.

_CLEAR_FILE_UI = 'DELETE FROM files WHERE filename = :filename'

_INSERT_FILE_UI = '''
INSERT INTO files (filename, ui) VALUES (:filename, :ui);'''

_INSERT_WINDOW_UI = 'INSERT INTO windows (fid, ui) VALUES (:fid, :ui);'

_GET_FILE_UI = 'SELECT fid, ui FROM files WHERE filename = :filename;'

_GET_WINDOW_UI = 'SELECT ui FROM windows WHERE fid = :fid;'
