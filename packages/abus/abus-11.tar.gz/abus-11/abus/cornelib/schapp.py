# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import argparse
import os.path
import re
import sqlite3
import sys
from   typing import Callable, Iterable, List, Optional, Tuple
import unittest

from .misc import set_indentation

def schapp_main(args:List[str]) -> None:
   """Upgrades a database to target schema given command line parameters"""
   parser= argparse.ArgumentParser(
      prog= os.path.basename(args[0]),
      description="""Schapp applies a target schema to a database, adjusting the
                     database schema to comply with target while migrating existing data.""",
      )
   parser.add_argument('-s', '--schema',
      metavar='<schema script>',
      dest='schema_path',
      required=True,
      help="""Path to SQL file defining the target schema""")
   parser.add_argument('-d', '--db',
      metavar='<database path>',
      dest='db_path',
      required=True,
      help="""Path to database being upgraded""")
   parser.add_argument('upgrade_files', nargs='*', metavar='<upgrade script>',
      help="""Paths to upgrade SQL files that migrate a database with
            schema version 1, schema version 2, etc, respectively, to the target schema""")
   cmdline_args= parser.parse_args(args[1:])

   with sqlite3.connect(cmdline_args.db_path) as conn:
      upgrader= Schapp(conn, cmdline_args.schema_path, cmdline_args.upgrade_files)
      upgrader.perform_upgrade(conn)

class Schapp(object):
   def __init__(self,
        conn: sqlite3.Connection,
        schema_file_path: str,
        upgrade_file_paths: List[str],
        legacy_version_function: Optional[Callable[[sqlite3.Connection], str]]= None):
      """
      Creates a database upgrader. Call `perform_upgrade` method to upgrade the database to the target schema.
      This constructor checks existing versions and finds the target version but does not yet make any changes.

      :param conn: used for inspecting the current version of the database

      :param schema_file_path: points to a script with schapp-complient syntax that defines the target schema.
         The script must contain a comment of the form "-- schapp schema version <version_string>" for schapp to determine
         if any given database needs upgrading. The version_string must start with digits up to the first '.' (or be only
         digits if there is no '.') which as an int form the *major version* which must be at least 1.

      :param upgrade_file_paths: Paths to scripts upgrading from current major version to target schema.
         The first entry upgrades version 1->target, then 2->target etc.
         There must therefore be exactly one element less than the target major version defined inside the schema file.

      :param legacy_version_function: Function that given the open connection returns the database's version.
         Schapp reads the pre-upgrade schema version from the _database_version table in the database. If there is no such
         table, `legacy_version_function` is called (if given) to determine what the current version is. This allows upgrading
         from old versions that were not created with schapp. Without the function a missing _database_version table
         implies that the current database is blank (version "0").
      """
      self._schema_file_path= schema_file_path
      with open(schema_file_path) as stream:
         m= re.search(r"-- schapp schema version ((\d+)([.]\d+)?)", stream.read())
      if m is None:
         raise Exception('Could not find schapp schema version in schema file - expect line of form "-- schapp schema version 0.0"')
      self._target_version= m.group(1)
      self._target_major= int(m.group(2))

      if len(upgrade_file_paths) != self._target_major-1:
         raise Exception("Expected exactly {} upgrade scripts, first one to upgrade schema 1 to schema {}, etc.".format(
                 self._target_major - 1, self._target_major))

      try:
         self._current_version= conn.execute("select current_version from _database_version").fetchall()[0][0]
      except sqlite3.OperationalError as e:
         if legacy_version_function is not None:
            self._current_version= legacy_version_function(conn)
         else:
            self._current_version= "0"
      self._current_major= int(self._current_version.partition(".")[0])
      if self._current_major>self._target_major:
         raise Exception("Current database version is greater than target schema version")
      if 0 < self._current_major < self._target_major:
         self._upgrade_file= upgrade_file_paths[self._current_major - 1]
      else:
         self._upgrade_file= None # upgrade to target schema from same major

   @property
   def requires_upgrade(self) -> bool:
      return self._current_version != self._target_version

   @property
   def preupgrade_major_version(self) -> int:
      return self._current_major

   def perform_upgrade(self, db_conn: sqlite3.Connection) -> None:
      """
      Performs the required upgrade:

      - Creates all new column from schema, leaving all existing ones (even if not in new schema)
      - Drops all constraints
      - Runs given upgrade script which is expected to populate new columns and clear old ones.
      - Drops all old columns, checking they are now empty.
      - Creates all constraints, views, and triggers.

      :param db_conn: this may be a different connection from the one used at construction but must obviously be to
      the same database.
      """
      if not self.requires_upgrade:
         return

      table_defs, trigger_defs, pass_through_defs= read_new_schema(self._schema_file_path)
      version_table= tabledef_from_statementlines([
         "create table _database_version(",
         "  current_version text not null,",
         "  constraint only_one_row check(rowid==1)"
         ");"])
      table_defs.append(version_table)
      existing_tables= set(drop_programmability(db_conn))
      drop_constraints(existing_tables, table_defs, db_conn)

      # Running the appropriate upgrade script to upgrade FROM the current version to head.
      if self._upgrade_file is not None:
         errors= False
         for stmt_lines in read_clean_statements(self._upgrade_file):
            for row in db_conn.execute("\n".join(stmt_lines)):
               print(row)
               errors= True
         if errors: raise Exception("there was integrity checking output")

      create_constraints(table_defs, existing_tables, db_conn)
      create_programmability(trigger_defs, pass_through_defs, db_conn)
      db_conn.execute("pragma foreign_keys= on;")
      violations= db_conn.execute("pragma foreign_key_check;").fetchall()
      if violations:
         raise Exception("FK violations: " + "\n  ".join(repr(row) for row in violations))
      if db_conn.execute("select * from _database_version").fetchall():
         db_conn.execute("update _database_version set current_version= ?", [self._target_version])
      else:
         db_conn.execute("insert into _database_version select ?", [self._target_version])


# [[[cog
# import cornelib
# make_struct= lambda cls,docstr: cornelib.cog_make_struct_type(cog.outl, cls, docstr)
#
# make_struct("Tabledef", '''The should-definition of a table.
#
# Args:
#   name (unicode): table name
#   statement_lines (list[unicode]): The create-statement split into lines.
#   column_types (dict[unicode, unicde]): column_name -> type for all columns in create-statement.
# ''')
#]]]
class Tabledef(object):
   # This is cog-generated code, make changes in the cog-comment above.
   @property
   def name(self):
      return self._name
   @property
   def statement_lines(self):
      return self._statement_lines
   @property
   def column_types(self):
      return self._column_types
   def __repr__(self):
      fields= ", ".join([
            "name="+repr(self._name),
            "statement_lines="+repr(self._statement_lines),
            "column_types="+repr(self._column_types),
         ])
      return "Tabledef({})".format(fields)
   # noinspection PyProtectedMember
   def __eq__(self, other):
      return (isinstance(other, Tabledef)
         and self._name == other._name
         and self._statement_lines == other._statement_lines
         and self._column_types == other._column_types
         )
   def __init__(self,
                name,
                statement_lines,
                column_types,
                ):
      """
      The should-definition of a table.

      Args:
        name (unicode): table name
        statement_lines (list[unicode]): The create-statement split into lines.
        column_types (dict[unicode, unicde]): column_name -> type for all columns in create-statement.
      """
      self._name= name
      self._statement_lines= statement_lines
      self._column_types= column_types
      assert isinstance(name, str)
      assert isinstance(statement_lines, list)
      assert isinstance(column_types, dict)
# [[[end]]]

def start_is_in(s, *beginnings):
   return any(s.lower().startswith(b+" ") for b in beginnings)

def read_clean_statements(script_path):
   """
   Returns iterable of SQL statements from given script file.

   :return: SQL lines forming one statement
   :rtype: str list
   """
   statement= []
   is_block= False
   with open(script_path) as input_stream:
      for line in input_stream:
         if line.strip()=="EOF":
            break
         line= line.rstrip()
         stripped= re.sub(r"\s*(--.*)?$", "", line.strip())
         if stripped or statement:
            statement.append(line)
            if stripped=="begin":
               is_block= True
            if stripped.endswith(";") and (not is_block or stripped=="end;"):
               yield statement
               statement= []
               is_block= False
   if statement:
      raise Exception("incomplete input stream, remaining code: "+" \n".join(statement))

def tabledef_from_statementlines(statement):
   first_line= statement[0]
   if not first_line.endswith("("):
      raise Exception("create table line does not end with '(': "+repr(first_line))
   table_name= first_line[:-1].split()[2]
   column_line_matches= (re.match(r"\s*(\w+)\s+(\w+)\W", line) for line in statement)
   column_types= { m.group(1):m.group(2)
                   for m in column_line_matches
                   if m and m.group(1).lower() not in{"create", "constraint"}
                 }
   return Tabledef(table_name, statement, column_types)

def read_new_schema(schema_script_path):
   """

   Returns: tuple of
     table_defs: Tabledef list
     trigger_defs: statement lines for triggers
     pass_through_defs: statement lines for other objects
   """
   trigger_defs= []
   pass_through_defs= []
   table_defs= []
   for statement in read_clean_statements(schema_script_path):
      first_line= statement[0]
      if start_is_in(first_line, "create table"):
         tabledef= tabledef_from_statementlines(statement)
         table_defs.append(tabledef)
      elif start_is_in(first_line, "create view", "create index", "create unique index"):
         pass_through_defs.append(statement)
      elif start_is_in(first_line, "create triggers"):
         trigger_defs.append(statement)
      else:
         raise Exception('cannot handle "{}"'.format(first_line))
   return table_defs, trigger_defs, pass_through_defs

def drop_programmability(db_conn: sqlite3.Connection) -> Iterable[str]:
   """removes all database objects except tables and returns list of the existing tables
   """
   rs= db_conn.execute("""select type, name
      from sqlite_master
      where not (type='index' and name like 'sqlite^_autoindex^_%' escape '^')""").fetchall()
   for typ, name in rs:
      if typ.lower() in {"trigger", "view", "index"}:
         db_conn.execute("drop {} {};".format(typ, name))
      elif typ.lower()=="table":
         yield name
      else:
         raise Exception("cannot handle {} object".format(typ))

def drop_constraints(existing_tables, new_tabledefs, db_conn: sqlite3.Connection) -> None:
   """
   drops all constraints from existing tables and creates all new columns while leaving all existing columns

   :param existing_tables: names of
   :type existing_tables: str set
   :param new_tabledefs: definitions of all tables to which is being upgrade
   :type new_tabledefs: Tabledef list
   """
   def make_tabledef(name, column_types):
      prev= "create table {}(".format(name)
      for colname,typ in column_types.items():
         yield prev
         prev= "  {} {},".format(colname,typ)
      yield prev.replace(",", ");")
   db_conn.execute("pragma foreign_keys= off;")
   new_column_types= { td.name:td.column_types for td in new_tabledefs }
   for table_name in existing_tables:
      existing_columns_result_set= db_conn.execute("pragma table_info('{}')".format(table_name)).fetchall()
      existing_column_names= [t[1] for t in existing_columns_result_set]
      old_and_new_column_types= {colname:coltype for (_i, colname, coltype, _notnull, _default, _pk) in existing_columns_result_set}
      if table_name in new_column_types:
         old_and_new_column_types.update(new_column_types[table_name])
      statement_lines= make_tabledef(table_name, old_and_new_column_types)
      hide_table(table_name, db_conn)
      recreate_table(table_name, statement_lines, existing_column_names, db_conn)
   for tabledef in new_tabledefs:
      if tabledef.name not in existing_tables:
         statement_lines= make_tabledef(tabledef.name, tabledef.column_types)
         db_conn.execute("\n".join(statement_lines))

def hidden_table_name(original_table_name):
   pfx= "_copy_of_"
   assert not original_table_name.startswith(pfx)
   return pfx+original_table_name

def hide_table(table_name: str, db_conn: sqlite3.Connection) -> None:
   db_conn.execute("alter table {} rename to {};".format(table_name, hidden_table_name(table_name)))

def recreate_table(table_name, statement_lines, copy_columns_list, db_conn: sqlite3.Connection) -> None:
   """
   Creates a table and copies existing data from hidden table.

   :param table_name: name of new table and indirectly of hidden table to be copied
   :type table_name: str
   :param statement_lines: SQL statement that creates the table
   :type statement_lines: str list
   :param copy_columns_list: columns that will be included in the data-copy
   :type copy_columns_list: str iterable
   """
   db_conn.execute("\n".join(statement_lines))
   columns_string= ", ".join(copy_columns_list)
   hidden= hidden_table_name(table_name)
   db_conn.execute("insert into {n}({l})\n  select {l}\n  from {h};".format(n=table_name, l=columns_string, h=hidden))
   db_conn.execute("drop table {};".format(hidden))

def create_constraints(table_defs, existing_tables, db_conn: sqlite3.Connection) -> None:
   new_table_names= set(t.name for t in table_defs)
   for table_name in new_table_names:
      hide_table(table_name, db_conn)
   for table_def in table_defs:
      recreate_table(table_def.name, table_def.statement_lines, table_def.column_types.keys(), db_conn)
   for t in set(existing_tables) - new_table_names:
      db_conn.execute("drop table {};".format(t))

def create_programmability(trigger_defs,
                           pass_through_defs,
                           db_conn: sqlite3.Connection) -> None:
   for statement_lines in pass_through_defs:
      db_conn.execute("\n".join(statement_lines))
   for i, statement_lines in enumerate(trigger_defs):
      _create, _triggers, table_name, columns = statement_lines[0].split(None, 3)
      core_statement= "\n      ".join(statement_lines[1:])
      for insert_update in ("insert", "update of "+columns):
         sql= set_indentation(0, """
            create trigger {table}_{i}{iu}
               before {insert_update} on {table}
               for each row
            {statement}""")
         db_conn.execute(sql.format(i= i,
                                 iu= insert_update[0],
                                 insert_update= insert_update,
                                 table= table_name,
                                 statement= core_statement,
                                 ))
      # getting trigger to check existing data by creating it on dummy table and performing dummmy insert:
      db_conn.execute("create table tmpt(x int);")
      core_statement= re.sub(r"\b(OLD|NEW)\b", table_name, core_statement)
      core_statement= re.sub(r"\bfrom\b", "from {},".format(table_name), core_statement)
      sql= set_indentation(0, """
         create trigger tmptr
            before insert on tmpt
            for each row
         {}""".format(core_statement))
      db_conn.execute(sql)
      db_conn.execute("insert into tmpt values(0);")
      db_conn.execute("drop table tmpt;")


class _Test_Schapp_(unittest.TestCase):
   def test_tabledefs_ending_comma(self):
      script= set_indentation(0, """
         create table T(
            hello int,
            world text not null);""")
      tabledefs,triggers,other = read_new_schema(script)
      self.assertFalse(triggers)
      self.assertFalse(other)
      self.assertEqual(len(tabledefs), 1)
      t= tabledefs[0]
      self.assertEqual(t.name, "T")
      self.assertEqual(t.statement_lines, script.split("\n"))
      self.assertEqual(t.column_types, {'hello':'int', 'world':'text'})
