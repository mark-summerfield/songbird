#!/bin/bash
cd src
tokei -slines -c80 -tPython
unrecognized.py -q
python3 -m flake8 --config=setup.cfg . 
python3 -m vulture . | grep -v '60%.confidence'
cd ..
git st
