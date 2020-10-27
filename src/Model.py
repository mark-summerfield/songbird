#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import apsw


class Model:

    def __init__(self, filename=None):
        self.db = None
        if filename is None:
            self._filename = None
        else:
            self._open(filename)


    def __bool__(self):
        return self.db is not None


    @property
    def filename(self):
        return self._filename


    def _open(self, filename):
        self.close()
        self._filename = filename
        self.db = apsw.Connection(str(filename))


    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
            self._filename = None
