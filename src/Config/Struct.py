#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import collections


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


    def __str__(self): # debug
        parts = [f'''Db={self.filename}
    mdi={self.mdi}
    show_items_tree={self.show_items_tree}
    show_pragmas={self.show_pragmas}
    show_calendar={self.show_calendar}
    show_items_tree={self.show_items_tree}''']
        for window in self.windows:
            parts.append(f'        {window}')
        return '\n'.join(parts)


class DbWindowUi:

    def __init__(self, title, sql_select, *, x=None, y=None, width=None,
                 height=None, editor_height=None):
        self.title = title
        self.sql_select = sql_select
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.editor_height = editor_height


    def __str__(self): # debug
        sql = ' '.join(self.sql_select.split()).strip()
        return (f'window={self.title} ({self.x},{self.y}+{self.width}+'
                f'{self.height}) {self.editor_height} {sql!r}')