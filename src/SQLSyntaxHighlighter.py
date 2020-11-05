#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor, QSyntaxHighlighter

# See /home/mark/commercial/zOld/comparedir1/PythonEditor.py

class SQLSyntaxHighlighter(QSyntaxHighlighter):

    def __init__(self, parent=None):
        super().__init__(parent)


    def highlightBlock(self, text):
        # TODO
        # 1. 'strings' including 'strings with '' quotes'
        # 2. "names of things"
        # 3. -- comments to EOL and /* long comments */
        # 4. SQL language:
        #   ALTER\s+TABLE
        #   ANALYZE
        #   BEGIN(:?\s+TRANSACTION)?
        #   CREATE\s+(:?(:?VIRTUAL\s+)?TABLE)|INDEX|TRIGGER|VIEW)
        #   ...
        # 5. SQLite functions:
        #   AVG(?=\()
        #   COUNT(?=\()
        #   ...
        # 6. SQL keywords:
        #   ABORT
        #   ACTION
        #   ...
        # 7. Constants:
        #   TRUE
        #   FALSE
        #   NULL
        print('highlightBlock', text)


    def rehighlight(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        QSyntaxHighlighter.rehighlight(self)
        qApp.restoreOverrideCursor()
