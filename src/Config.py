#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib

import apsw

from Const import APPNAME, WIN


def get(path=None):
    if get.config is None:
        get.config = _Config(path)
    return get.config
get.config = None # noqa


class _Config:

    def __init__(self, path):
        self.path = path
        self.filename = _get_filename(path)



def _get_filename(path):
    name = APPNAME.lower() + '.sbc'
    if WIN:
        names = [pathlib.Path.home() / name, path / name]
        index = 0
    else:
        names = [pathlib.Path.home() / '.config' / name,
                 pathlib.Path.home() / f'.{name}', path / name]
        index = 0 if (pathlib.Path.home() / '.config').is_dir() else 1
    for name in names:
        if name.exists():
            return name.resolve()
    name = names[index].resolve()
    _make_default_sbc(name)
    return name


def _make_default_sbc(name):
    print(f'_make_default_sbc {name}')
