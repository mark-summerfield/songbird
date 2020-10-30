#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib


def get(limit=9): # The limit is only used the very first time
    if get.recent_files is None:
        get.recent_files = _Singleton_RecentFiles(limit)
    return get.recent_files
get.recent_files = None # noqa


class _Singleton_RecentFiles:

    def __init__(self, limit):
        self.limit = limit
        self._filenames = [] # possibly empty list of pathlib.Path
        self._current = None # None or pathlib.Path


    @property
    def current(self):
        return self._current


    def add(self, name):
        if self._current:
            self._filenames.append(self._current)
        self._current = pathlib.Path(name).resolve()


    def load(self, names):
        self.clear()
        seen = {self.current} if self.current else set()
        for name in reversed(names):
            filename = pathlib.Path(name).resolve()
            if filename not in seen and filename.exists():
                seen.add(filename)
                self._filenames.append(filename)


    def __iter__(self):
        seen = {self.current} if self.current else set()
        count = 0
        for filename in reversed(self._filenames):
            if filename not in seen and filename.exists():
                if count >= self.limit:
                    break
                count += 1
                seen.add(filename)
                yield filename


    def clear(self):
        self._filenames.clear()
