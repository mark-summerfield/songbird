#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from Const import (
    LAST_FILE, MAIN_WINDOW_GEOMETRY, MAIN_WINDOW_STATE, OPENED, RECENT_FILE,
    SHOW_AS_TABS, SHOW_ITEMS_TREE, SHOW_PRAGMAS)

_VERSION = 7

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
INSERT INTO config (key, value) VALUES ('{SHOW_ITEMS_TREE}', TRUE);
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
