#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from Const import (
    LAST_FILE, MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE, OPENED, RECENT_FILE,
    SHOW_AS_TABS, SHOW_ITEMS_TREE, SHOW_PRAGMAS)

_VERSION = 8

_PREPARE = f'''
PRAGMA encoding = 'UTF-8';
PRAGMA foreign_keys = TRUE;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
'''

_CREATE = f'''
PRAGMA user_version = {_VERSION};

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
    mdi INTEGER DEFAULT TRUE NOT NULL,
    show_items_tree INTEGER DEFAULT TRUE NOT NULL,
    show_pragmas INTEGER DEFAULT FALSE NOT NULL,
    show_calendar INTEGER DEFAULT FALSE NOT NULL,

    CHECK(mdi IN (0, 1)),
    CHECK(show_items_tree IN (0, 1)),
    CHECK(show_pragmas IN (0, 1)),
    CHECK(show_calendar IN (0, 1))
);

CREATE TABLE windows (
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
