#!/bin/bash
cd src
tokei -f -slines -c110 -tPython -eAppData.py
unrecognized.py -q
python3 -m flake8 --config=../setup.cfg --exclude AppData.py . \
    | grep -v undefined.name..qApp
python3 -m vulture --exclude AppData.py . \
    | grep -v '60%.confidence' \
    | grep -v MainWindow.__init__.py.*unused.import
cd ..
git st
