# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from   contextlib import contextmanager
import logging
import os.path
import queue
import re
import shutil
import sqlite3
import sys

from abus.cornelib import Schapp
from abus.database_backup_restore import DatabaseBackupRestoreMixin
from abus.database_purge import DatabasePurgeMixin
from abus.database_rebuild import DatabaseRebuildMixin
from abus.rebuild import find_index_files, find_compressed_backups

class connect:
   def __init__(self, database_path, archive_root_path, allow_create=False):
      """
      Returns an object for the index database.

      :param database_path:
      :param allow_create: whether blank database should be created if `database_path` does not exist.
      :rtype: Database
      """
      self.db= Database(database_path, archive_root_path, allow_create)
   def __enter__(self):
      return self.db
   def __exit__(self, exc_type, exc_val, exc_tb):
      self.db.close()

class Database(DatabaseBackupRestoreMixin, DatabasePurgeMixin, DatabaseRebuildMixin):
   def __init__(self, database_path, archive_root_path, allow_create):
      self.dbpath= database_path
      existed= os.path.exists(database_path)
      if not existed and not allow_create:
         raise RuntimeError("could not find database "+database_path)
      self.connection_pool_size= 0
      self.connection_pool= queue.Queue()
      self._set_connection_pool_size(1)
      self._check_schema(archive_root_path)
   def close(self):
      self._set_connection_pool_size(0)

   def _set_connection_pool_size(self, n):
      while self.connection_pool_size < n:
         conn= sqlite3.connect(self.dbpath, timeout=60, check_same_thread=False)
         conn.isolation_level= None # autocommit
         conn.execute("PRAGMA synchronous=OFF")
         self.connection_pool.put(conn)
         self.connection_pool_size += 1
      while self.connection_pool_size > n:
         self.connection_pool.get().close()
         self.connection_pool_size -= 1

   @contextmanager
   def _get_connection(self) -> sqlite3.Connection:
      """
      Returns a connection object from the pool with context manager.
      """
      conn= self.connection_pool.get()
      try:
         yield conn
      finally:
         self.connection_pool.put(conn)

   def _check_schema(self, archive_root_path):
      abus_src_dir= os.path.dirname(__file__)
      schema_file_path= abus_src_dir+"/schema.sql"
      upgrade_file_name_pattern= re.compile(r"upgrade-([0-9]+)[.]sql")
      upgrade_file_paths= sorted(
         direntry.path for direntry in os.scandir(abus_src_dir)
         if upgrade_file_name_pattern.match(direntry.name))

      def get_legacy_version(conn: sqlite3.Connection) -> str:
         """Returns script that backfills DB version, if necessary"""
         # did not have version table in versions <= 2.4, may need to find out manually if version is 0,1,or 2
         tables= set(conn.execute("select name from sqlite_master where type='table'").fetchall())
         if ("completed_run",) in tables:
            return "2"
         elif ("run",) in tables:
            return "1"
         else:
            return "0" # blank database

      with self._get_connection() as conn:
         schapp= Schapp(conn, schema_file_path, upgrade_file_paths, get_legacy_version)
         if not schapp.requires_upgrade:
            return

      logging.info("index database needs upgrading")
      print("index database needs upgrading - this may take a while", file=sys.stderr)
      with self._take_backup():
         with self._get_connection() as conn:
            schapp.perform_upgrade(conn)
            if 0 < schapp.preupgrade_major_version < 3:
               # need to fill-in new columns from archive directory scan
               logging.info("reconstructing new index data")
               print("reconstructing new index data", file=sys.stderr)
               data= ((archive_dir, run_name) for run_name,archive_dir in find_index_files(archive_root_path))
               conn.executemany("update run set archive_dir= ? where run_name = ?", data)
               data= ((checksum,) for checksum in find_compressed_backups(archive_root_path))
               conn.executemany("update location set is_compressed= 1 where checksum = ?", data)

   @contextmanager
   def _take_backup(self):
      """Context manager that creates a backup copy of the database and
      restores or deletes it on exit
      depending on whether an exception has been raised"""
      connection_pool_size= self.connection_pool_size
      self._set_connection_pool_size(0)
      backup= self.dbpath + ".backup"
      logging.info("taking backup of index database")
      shutil.copyfile(self.dbpath, backup)
      self._set_connection_pool_size(1)
      try:
         yield
      except:
         self._set_connection_pool_size(0)
         logging.info("index database upgrade failed, restoring backup")
         shutil.copyfile(backup, self.dbpath)
         os.unlink(backup)
         raise
      else:
         os.unlink(backup)
         self._set_connection_pool_size(connection_pool_size)
