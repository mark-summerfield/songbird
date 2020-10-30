#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import sys

APPNAME = 'Songbird'
BLINK = 'Blink' # Make this a user option
LAST_FILE = 'LastFile'
MAIN_WINDOW_GEOMETRY = 'MainWindow/Geometry'
MAIN_WINDOW_STATE = 'MainWindow/State'
OPENED = 'Opened'
RECENT_FILE = 'RecentFile'
RECENT_FILES_MAX = 9
SHOW_CONTENTS = 'ShowContents'
SHOW_PRAGMAS = 'ShowPragmas'
SUFFIXES = ('.sqlite', '.sqlite3', '.db', '.db3')
SUFFIX = '.sb'
DEFAULT_SUFFIX = SUFFIXES[0] # Make this a user option
TIMEOUT_LONG = 10000 # 10s
TIMEOUT_SHORT = 5000 # 5s
WIN = sys.platform.startswith('win')
