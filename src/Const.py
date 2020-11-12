#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import sys

APPNAME = 'Songbird'
LAST_FILE = 'LastFile'
MAIN_WINDOW_GEOMETRY = 'MainWindow/Geometry'
MAIN_WINDOW_STATE = 'MainWindow/State'
MAX_I32 = (2**31) - 1
OPENED = 'Opened'
RECENT_FILE = 'RecentFile'
RECENT_FILES_MAX = 9
SHOW_AS_TABS = 'ShowAsTabs'
SHOW_ITEMS_TREE = 'ShowItemsTree'
SHOW_PRAGMAS = 'ShowPragmas'
SUFFIX = '.sb'
SUFFIXES = ('.sqlite', '.sqlite3', '.db', '.db3')
SUFFIX_DEFAULT = SUFFIXES[0] # Make this a user option
TIMEOUT_LONG = 10000 # 10s
TIMEOUT_SHORT = 5000 # 5s
UNCHANGED = object()
WIN = sys.platform.startswith('win')
