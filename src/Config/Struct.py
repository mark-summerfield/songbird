#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import collections
import json


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

    def __init__(self, filename, *, mdi=True, show_items_tree=True,
                 show_pragmas=False, show_calendar=False, windows=None):
        self.filename = filename
        self.mdi = mdi
        self.show_items_tree = show_items_tree
        self.show_pragmas = show_pragmas
        self.show_calendar = show_calendar
        self.windows = [] if windows is None else windows


    @property
    def to_json(self): # Deliberately excludes filename and windows
        return json.dumps(dict(mdi=self.mdi,
                               show_items_tree=self.show_items_tree,
                               show_pragmas=self.show_pragmas,
                               show_calendar=self.show_calendar))


    def update(self, d):
        self.mdi = d.get('mdi', True)
        self.show_items_tree = d.get('show_items_tree', True)
        self.show_pragmas = d.get('show_pragmas', False)
        self.show_calendar = d.get('show_calendar', False)


class DbWindowUi:

    def __init__(self, title, sql_select, *, x=None, y=None, width=None,
                 height=None, sizes=None):
        self.title = title
        self.sql_select = sql_select
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sizes = sizes


    @property
    def to_json(self):
        return json.dumps(dict(title=self.title, sql_select=self.sql_select,
                               x=self.x, y=self.y, width=self.width,
                               height=self.height, sizes=self.sizes))
