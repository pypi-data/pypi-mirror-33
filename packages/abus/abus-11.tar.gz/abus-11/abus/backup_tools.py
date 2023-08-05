# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from   contextlib import contextmanager
import os
import queue
import threading
import time
from   typing import Dict

from abus import crypto
from abus import database

class IndexFile(object):
   """Open .lst file for recording all new backups. Use static `open` to create with context manager.
   Use `add_entry` for each new backup file."""
   def __init__(self, stream):
      self.lock= threading.Lock()
      self.stream= stream
   def add_entry(self, checksum, timestamp, path):
      with self.lock:
         print(checksum, timestamp, path, file=self.stream)
   @staticmethod
   @contextmanager
   def open(run_name, cfg, archive_dir):
      """Returns new `IndexFile` in a context manager"""
      d= cfg.archive_root_path+ "/"+archive_dir
      index_file_path= d+ "/"+run_name+".lst"
      partial_path= index_file_path+".part"
      os.makedirs(d, exist_ok=True)
      try:
         with crypto.open_txt(partial_path, "w", cfg.password) as stream:
            yield IndexFile(stream)
      except:
         os.unlink(partial_path)
         raise
      else:
         os.rename(partial_path, index_file_path)

class DeletionTracker(object):
   def __init__(self, indexdb:database.Database):
      """Creates list of all paths of original files known from previous backup runs.

      The caller removes paths that still exist in the current backup run using `seen()`;
      this identifies paths that have been deleted since the previous backup run.

      At the end of the current (successful) backup run the caller calls `complete()` which
      marks the paths not previusly `seen()` as deleted."""
      self.all_files= set(indexdb.get_undeleted_files())
      self.indexdb= indexdb
   def seen(self, path: str) -> None:
      """Marks a path as definitely existing"""
      self.indexdb.unmark_deleted(path)
      self.all_files.discard(path)
   def complete(self, index_file):
      """Marks all paths not previously seen() as deleted in the given index file as well as in the
      index database provided at construction of `self`.

      N.B.: This must only be called if the caller is sure that all existing paths have been `seen()`"""
      if self.all_files:
         t= time.time()
         for p in self.all_files:
            index_file.add_entry("deleted", t, p)
         self.indexdb.mark_deleted(t, self.all_files)

def read_blocks(stream):
   """returns contents of binary files as list of byte-blocks"""
   block_size= 8192
   while True:
      block= stream.read(block_size)
      yield block
      if len(block) < block_size:
         break

class ArchiveDirsToUse(object):
   """see __init__ for class docs"""
   def __init__(self, initial_subdir_usage: Dict[str,int]):
      """Constructs list of spaces in archive subdirectories available for new backup files.

      Usage::

         for file in files_in_need_of_backup():
            achive_dir= archive_dirs_to_use.get()
            backup(file, dest= archive_dir)

      In the event of an exception that prevents the creation of the backup file
      the space in the archive directory can be "returned"::

         for file in files_in_need_of_backup():
            with archive_dirs_to_use.get_returnable() as archive_dir:
               backup(file, dest= archive_dir)

      :param initial_subdir_usage: existing archive_dir -> n files therein
      """
      self.returns= queue.Queue() # dirs that were returned by get_returnable()
      self.sequence= self._sequence(initial_subdir_usage) # actual list of spaces
   def get(self) -> str:
      """Returns an archive subdirectory (relative to archive root) with space for one more backup files
      and reserves that space. The subdirectory returned need not exist, i.e. when all existing directories
      are full, a completely new one is returned."""
      try:
         return self.returns.get_nowait()
      except queue.Empty:
         return next(self.sequence)
   @contextmanager
   def get_returnable(self):
      """Returns an archive subdirectory like get(), but in a context manager, which returns the space on Exception."""
      archive_dir= self.get()
      try:
         yield archive_dir
      except:
         self.returns.put(archive_dir)
         raise
   @staticmethod
   def _sequence(initial_subdir_usage):
      files_per_dir= 100
      # returning existing subdirectories once for each of their spaces
      for archive_dir, n in initial_subdir_usage.items():
         for _ in range(n, files_per_dir):
            yield archive_dir
      # Returning new subdirectories, now that all existing ones are full.
      # Going through all integers, turning each into a subdirectory path.
      def mkpath(n):
         least= "{:02}".format(n%100)
         return least if n<100 else least + "/" + mkpath(n//100)
      n= -1
      while True:
         n += 1
         archive_dir= mkpath(n)
         if archive_dir not in initial_subdir_usage:
            for _ in range(files_per_dir):
               yield archive_dir
