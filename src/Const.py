#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import sys

APPNAME = 'Songbird'

WIN = sys.platform.startswith('win')

TIMEOUT_LONG = 10000 # 10s
TIMEOUT_SHORT = 5000 # 5s

RECENT_FILES_MAX = 9

BLINK = 'Blink'
LAST_FILE = 'LastFile'
MAIN_WINDOW_GEOMETRY = 'MainWindow/Geometry'
MAIN_WINDOW_STATE = 'MainWindow/State'
OPENED = 'Opened'
RECENT_FILE = 'RecentFile'
