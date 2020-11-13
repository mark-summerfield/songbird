#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import enum
import re

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

from Const import WIN

CONSTANTS = ('TRUE', 'FALSE', 'NULL')
FUNCTIONS = (
    'ABS', 'AVG', 'CHANGES', 'CHAR', 'COALESCE', 'COUNT', 'DATE',
    'DATETIME', 'GROUP_CONCAT', 'HEX', 'IFNULL', 'IIF', 'INSTR',
    'JULIANDAY', 'LAST_INSERT_ROWID', 'LENGTH', 'LIKELIHOOD', 'LIKELY',
    'LOAD_EXTENSION', 'LOWER', 'LTRIM', 'MAX', 'MIN', 'NULLIF', 'PRINTF',
    'QUOTE', 'RANDOM', 'RANDOMBLOB', 'REPLACE', 'ROUND', 'RTRIM', 'SOUNDEX',
    'SQLITE_COMPILEOPTION_GET', 'SQLITE_COMPILEOPTION_USED',
    'SQLITE_OFFSET', 'SQLITE_SOURCE_ID', 'SQLITE_VERSION', 'STRFTIME',
    'SUBSTR', 'SUM', 'TIME', 'TOTAL', 'TOTAL_CHANGES', 'TRIM', 'TYPEOF',
    'UNICODE', 'UNLIKELY', 'UPPER', 'ZEROBLOB')
KEYWORDS = (
    'ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ALWAYS', 'ANALYZE',
    'AS', 'ASC', 'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN',
    'BY', 'CASCADE', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT',
    'CONFLICT', 'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT', 'CURRENT_DATE',
    'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'DATABASE', 'DEFAULT',
    'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DO',
    'DROP', 'EACH', 'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUDE',
    'EXCLUSIVE', 'EXISTS', 'EXPLAIN', 'FAIL', 'FILTER', 'FIRST',
    'FOLLOWING', 'FOR', 'FOREIGN', 'FROM', 'FULL', 'GENERATED', 'GLOB',
    'GROUP', 'GROUPS', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE', 'INDEX',
    'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTERSECT',
    'INTO', 'ISNULL', 'JOIN', 'KEY', 'LAST', 'LEFT', 'LIKE', 'LIMIT',
    'NATURAL', 'NO', 'NOTHING', 'NOTNULL', 'NULLS', 'OF', 'OFFSET', 'ON',
    'ORDER', 'OTHERS', 'OUTER', 'OVER', 'PARTITION', 'PLAN', 'PRAGMA',
    'PRECEDING', 'PRIMARY', 'QUERY', 'RAISE', 'RANGE', 'RECURSIVE',
    'REFERENCES', 'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT',
    'RIGHT', 'ROLLBACK', 'ROW', 'ROWS', 'SAVEPOINT', 'SELECT', 'SET',
    'TABLE', 'TEMP', 'TEMPORARY', 'THEN', 'TIES', 'TO', 'TRANSACTION',
    'TRIGGER', 'UNBOUNDED', 'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM',
    'VALUES', 'VIEW', 'VIRTUAL', 'WHEN', 'WHERE', 'WINDOW', 'WITH',
    'WITHOUT') 
OPERATORS = ('IS', 'NOT', 'IN', 'LIKE', 'AND', 'OR', 'GLOB', 'MATCH',
             'REGEXP')


@enum.unique
class State(enum.IntEnum):
    CODE = 0
    COMMENT = 1


@enum.unique
class Syntax(enum.Enum):
    NORMAL = 0
    CONSTANT = 1
    FUNCTION = 2
    KEYWORD = 3
    NUMBER = 4
    OPERATOR = 5
    STRING = 6
    COMMENT = 7


class SQLSyntaxHighlighter(QSyntaxHighlighter):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.make_formats()


    def make_formats(self):
        self.formats = {}
        for kind, color in (
                (Syntax.NORMAL, Qt.black),
                (Syntax.CONSTANT, Qt.darkCyan),
                (Syntax.FUNCTION, Qt.blue),
                (Syntax.KEYWORD, Qt.darkBlue),
                (Syntax.NUMBER, Qt.darkRed),
                (Syntax.OPERATOR, Qt.darkMagenta),
                (Syntax.STRING, Qt.darkYellow),
                (Syntax.COMMENT, Qt.darkGreen)):
            fmt = QTextCharFormat()
            fmt.setFontFamily('Consolas' if WIN else 'Monospace')
            fmt.setFontFixedPitch(True)
            fmt.setFontStyleHint(QFont.Monospace)
            fmt.setForeground(QColor(color))
            if kind in {Syntax.CONSTANT, Syntax.FUNCTION, Syntax.KEYWORD,
                        Syntax.OPERATOR}:
                fmt.setFontCapitalization(QFont.AllUppercase)
                if kind is Syntax.KEYWORD:
                    fmt.setFontWeight(QFont.DemiBold)
            elif kind is Syntax.COMMENT:
                fmt.setFontItalic(True)
            self.formats[kind] = fmt


    def highlightBlock(self, text):
        state = State.CODE
        prev_state = State(max(self.previousBlockState(), State.CODE))
        i = 0
        self.setFormat(i, len(text), self.formats[Syntax.NORMAL])
        if prev_state is State.COMMENT:
            if (i := text.find('*/')) > -1: # found the end of the comment
                i += 2
                self.setFormat(0, i, self.formats[Syntax.COMMENT])
            else: # whole line is inside the comment
                self.setFormat(0, len(text), self.formats[Syntax.COMMENT])
                self.setCurrentBlockState(State.COMMENT)
                return # All in comments

        for pattern, syntax in (
                (r'\b' + f'({"|".join(CONSTANTS)})' + r'\b',
                 Syntax.CONSTANT),
                (r'\b' + f'(?P<func>{"|".join(FUNCTIONS)})(?=[(])',
                 Syntax.FUNCTION),
                (r'\b' + f'({"|".join(KEYWORDS)})' + r'\b', Syntax.KEYWORD),
                (r'\b(\d+(?:\.\d+)?|\.\d+)\b', Syntax.NUMBER),
                (r'([-+/%*"|<>&=!])', Syntax.OPERATOR),
                (r'\b' + f'({"|".join(OPERATORS)})' + r'\b',
                 Syntax.OPERATOR),
                (r"('[^']+?')", Syntax.STRING),
                (r'(/\*.*?\*/|--.*$)', Syntax.COMMENT),
                ):
            for match in re.finditer(pattern, text,
                                     re.IGNORECASE | re.DOTALL):
                start = max(i, match.start(1))
                end = match.end(1)
                if end >= start:
                    self.setFormat(start, end - start, self.formats[syntax])

        if (j := text.find('/*', i)) > -1:
            if (k := text.find('*/', j)) == -1: # Multi-line comment
                self.setFormat(j, len(text),    # started but not finished
                               self.formats[Syntax.COMMENT])
                self.setCurrentBlockState(State.COMMENT)
                return
        self.setCurrentBlockState(State.CODE)
