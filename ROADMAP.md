# Songbird Roadmap

## Roadmap

### 0.3.0 QueryWidget

- copy TableWidget.py to QueryWidget.py
- put TableView in a QWidgetStack? with a SQLEdit
- if query is SELECT then switch to the TableView and do as now;
- otherwise switch to the SQLEdit and do:
    ```python
    try:
	self.db.execute(sql)
    ...
    ```
- for queries, give the window the name "Query #n" (so for save/restore put
  windows with names matching `/Query #\d+/` under the queryItem)
- If this all works, then replace the TableWidget with the QueryWidget
- Make views and tables open with the editor _closed_ by default; and for
  queries open with the editor _open_ (as now)

### 0.3.5 File Menu incl. Import and Export

Complete the File menu, including import and export.

### 0.4.0 Column clicking ORDER BY

Clicking column name adds/replaces ORDER BY in SQLEdit for tables, views,
and queries

### 0.4.2 Database Menu insert/update/delete options

&Database |
--------- |
_New &Query_ |
................. |
_&Next Record_ |
_&Previous Record_ |
................. |
&Insert Record... |
&Update Record... |
&Delete Record... |
................. |
_&Alter..._ |
................. |
_&Create Form..._ |
_&Edit Form..._ |
_&Show Form..._ |
_Convert to &Songbird_ |

For Insert and Update create default forms.

(_Italicised_ options are to be implemented later; see below)

### 0.4.3 View→Show Row Numbers

&View→[X] Show &Row Numbers

This is per-window so needs to be saved/restore to/from JSON ui.

### 0.4.5 Database→New Query

&Database→New &Query...

Leads to a wizard for creating CREATE (tables, views, virtual tables,
indexes, triggers), SELECT, INSERT, UPDATE, DELETE, DROP, or unspecified SQL
statements. For Insert and Update use the default forms (see above)

### 0.5.0 Database→Alter

&Database→&Alter...

Leads to a wizard for altering tables, views, and triggers (and where SQL
ALTER won't work try to implement by renaming, creating, copying and
deleting)

### 0.5.5 File→Preferences

&File→&Preferences...

Create a suitable dialog

### 0.6.0 &Database→Convert to &Songbird

&Database→Convert to &Songbird

Add songbird\_config (equiv. of .sbc config & files), songbird\_windows, and
songbird\_types (tablename, fieldname, type), songbird\_forms tables.

This means implementing at least a few "rich" types and creating one default
form per table (accounting for FKs).

### 0.6.5 Database menu complete with custom forms for Songbird databases

&Database |
--------- |
&Next Record |
&Previous Record |
................ |
&Create Form... |
&Edit Form... |
&Show Form... |

Default and custom forms allow the user to do prev/next/insert/update/delete
(So update the Insert/Update/Delete menu options to work with forms as well
as rows in a QueryWidget)

### 0.7.0 SDI

&Window _(SDI - max of 9)_ |
----------------------- |
&1 _sdi name1_ |
_:_ |
&9 _sdi nameN_ |

### 0.7.5 Extra functionality

Add any functionality offered by DB Browser for SQLite that seems useful,
e.g., optimize, check, etc.

### 0.8.0 Rich types

Add any more rich types that are useful. This has an impact on custom and
default forms.

### 0.9.0


### 1.0.0

!

## Ideas

- provide an editor/dialog/? for creating transforms e.g., applying
  some math function to every column in a table (or selection of a
  table), etc.

- Completion in SQLEdit?

- A plugin system? (Using a PyPI lib'y?), e.g., to support:
  - Excel import/export using try .. except ImportError so it is
    available but not required
    (& similarly for dBase II, Access, etc., if suitable modules are
    available)
  - Songbird (& SQLite?) merge
  - ...

- implement Undo/Redo by using a temporary memory database; see
  https://www.sqlite.org/undoredo.html
