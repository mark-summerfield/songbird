#!/bin/bash
cd src
tokei -f -slines -c110 -tPython
unrecognized.py -q
python3 -m flake8 --config=../setup.cfg . \
    | grep -v undefined.name..qApp
python3 -m vulture . \
    | grep -v '60%.confidence' \
    | grep -v MainWindow.__init__.py.*unused.import
cd ..
git st
