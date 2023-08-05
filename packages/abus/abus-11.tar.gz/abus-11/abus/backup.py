# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import concurrent.futures
import enum
from   fnmatch import fnmatch
import hashlib
import logging
import os
import sys
import time
import traceback

from abus.cornelib import partial_write_guard
from abus import config
from abus import crypto
from abus import database
from abus import synchronisation
from abus.backup_tools import ArchiveDirsToUse, DeletionTracker, IndexFile, read_blocks

class Counters(enum.Enum):
   DIRS= "directories"
   UNTOUCHED= "untouched files"
   CHECKSUMMED_ONLY= "already backed up"
   COMPRESSED= "compressed"
   UNCOMPRESSED= "copied"
   ERROR= "errors"

def do_backup(cfg: config.Configuration, db: database.Database) -> None:
   """Performs a backup run with given configuration.
   """
   initial_subdir_usage= db.get_archivedir_usage()
   archivedirs_to_use= ArchiveDirsToUse(initial_subdir_usage)
   run_file_archive_dir= archivedirs_to_use.get()
   run_name= db.open_backup_run(run_file_archive_dir)
   logging.info("ABuS version {}, starting backup run {}".format(cfg.ABUS_VERSION, run_name))
   stats= {c:0 for c in Counters}
   deletion_tracker= DeletionTracker(db)
   backup_errors= False
   with IndexFile.open(run_name, cfg, run_file_archive_dir) as index_file:
      with concurrent.futures.ThreadPoolExecutor(cfg.n_threads) as executor:
         # This thread walks the directories, runs do_one_file in the background for each file
         # and waits for all the background tasks.
         futures= []
         dir_queue= list(cfg.include)
         while dir_queue:
            p= dir_queue.pop()
            try:
               direntries= os.scandir(p)
            except (PermissionError, OSError) as e:
               msg= str(e)
               displaydir= "" if p in msg else " "+p
               logging.error("Error reading directory%s: %s", displaydir, msg)
               stats[Counters.ERROR] += 1
               backup_errors= True
               continue
            else:
               stats[Counters.DIRS] += 1
            for direntry in direntries:
               path= direntry.path.replace('\\', '/')
               if any(fnmatch(path, p) for p in cfg.exclude):
                  pass
               elif direntry.is_file(follow_symlinks=False):
                  deletion_tracker.seen(path)
                  if len(futures) >= cfg.n_threads*2:
                     # prevents queue becoming too large by blocking this search thread before adding more backup files
                     wait_for_one(futures, stats)
                  f= executor.submit(do_one_file, direntry, run_name, archivedirs_to_use, cfg, db, index_file)
                  futures.append(f)
               elif direntry.is_dir(follow_symlinks=False):
                  dir_queue.append(path)
         while futures:
            wait_for_one(futures, stats)
      if not backup_errors:
         deletion_tracker.complete(index_file)
   logging.info(", ".join("{}: {}".format(c.value, n) for c,n in stats.items()))
   if stats[Counters.ERROR]==0:
      logging.info("completed backup run %s without errors", run_name)
   else:
      logging.warning("completed backup run %s with errors", run_name)
      raise RuntimeError("some files failed to be backed up")

def wait_for_one(futures, stats):
   done,not_done = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
   for f in done:
      stats[f.result()] += 1
   futures[:]= not_done

def calculate_checksum(path: str) -> str:
   """Calculates SHA256 sum of a file"""
   partially_calculated_checksum= hashlib.sha256()
   with open(path, "rb") as fd:
      for blk in read_blocks(fd):
         partially_calculated_checksum.update(blk)
   return partially_calculated_checksum.hexdigest()

class FileChangedWhileReadingError(Exception):
   pass

def do_one_file(direntry, run_name, archivedirs_to_use:ArchiveDirsToUse, cfg, db:database.Database, index_file:IndexFile):
   """
   Processes a single file, making appropriate database entries for it and creating the
   backup copy if necessary.

   :param direntry: a direntry with the file information as returned by os.scandir()
   :param run_name: the backup run to which the file should be added
   :param archivedirs_to_use: list of archive dirs (relative to archive root) with free spaces for n
                                   into which new backup copies should be placed.
   :type cfg: config.Configuration
   :type db: database.Database
   :param index_file: Open file descriptor for writing the index entry
   :type index_file: IndexFile
   """
   path= direntry.path.replace("\\", "/")
   try:
      stat= direntry.stat()
      if stat.st_dev==0 and stat.st_ino==0:
         # this means this is windows and the direntry does not have the relevant information
         stat= os.stat(path)

      failed_attempts= 0
      while True: # retry loop
         try:
            result= do_one_file_no_retry(run_name, path, stat, cfg, db, archivedirs_to_use, index_file)
         except FileChangedWhileReadingError:
            failed_attempts += 1
            if failed_attempts==5:
               raise RuntimeError("file changed while reading")
            time.sleep(failed_attempts)
            stat= os.stat(path)
         else:
            return result
   except Exception as e:
      index_file.add_entry("error", 0, path)
      log_error(e, direntry)
      return Counters.ERROR

def do_one_file_no_retry(run_name, path, stat, cfg, db:database.Database, archivedirs_to_use, index_file):
   with synchronisation.global_data_lock(path):
      if db.is_file_unchanged(path, stat.st_dev, stat.st_ino, stat.st_mtime, stat.st_ctime):
         result= Counters.UNTOUCHED
      else:
         checksum= calculate_checksum(path)

         with synchronisation.global_data_lock(checksum):
            if db.have_checksum(checksum):
               result= Counters.CHECKSUMMED_ONLY
            else:
               with archivedirs_to_use.get_returnable() as archive_dir:
                  if stat.st_size < cfg.minimum_size_for_compression or cfg.is_already_compressed(path):
                     ext= ""
                     open_dst_function= crypto.open_bin
                     result= Counters.UNCOMPRESSED
                     is_compressed= False
                  else:
                     ext= ".z"
                     open_dst_function= crypto.open_lzma
                     result= Counters.COMPRESSED
                     is_compressed= True
                  backup_path= cfg.mk_archive_path(archive_dir, checksum, ext)
                  make_backup_copy(path, checksum, backup_path, open_dst_function, cfg.password)
                  db.remember_archivedir(checksum, archive_dir, is_compressed)

         if db.add_backup_entry(run_name, path, stat.st_mtime, checksum):
            index_file.add_entry(checksum, stat.st_mtime, path)
         db.remember_file_metadata(path, stat.st_dev, stat.st_ino, stat.st_mtime, stat.st_ctime)
   return result

def log_error(e: Exception, direntry: os.DirEntry) -> None:
   """
   Issues as pretty an error message as possible

   :param e: error that is being logged
   :param direntry: of file that we tried to back up when exception occurred
   """
   #logging.debug("%s", "".join(traceback.format_exception(type(e), e, e.__traceback__)))
   if isinstance(e, RuntimeError):
      error_msg= str(e)
   else:
      error_msg= "".join(traceback.format_exception(type(e), e, e.__traceback__))
   path= direntry.path.replace("\\","/")
   if path.lower() not in error_msg.replace("\\","/").lower():
      error_msg= "While backing up {}: {}".format(path, error_msg)
   logging.error(error_msg)
   print(error_msg, file=sys.stderr)

def make_backup_copy(path, expected_checksum, backup_path, open_dst_function, password):
   """
   Creates the encrypted backup copy of a file, taking care not to leave a partial backup file in case of errors.

   :param path: Path of file to be backed up.
   :param expected_checksum: Known checksum of the file, which is verified while copying; if different, an exception
                             will be raised.
   :param backup_path: absolute filename of the destination file
   :param open_dst_function: function from crypto module to open the destination file, i.e. either open_lzma or open_bin
                             according to whether compression is required.
   :param password: to be used for encryption
   """
   os.makedirs(os.path.dirname(backup_path), exist_ok=True)
   partially_calculated_checksum= hashlib.sha256()
   with partial_write_guard(backup_path) as partial_path:
      with open(path,"rb") as src, open_dst_function(partial_path, "w", password) as dst:
         for blk in read_blocks(src):
            partially_calculated_checksum.update(blk)
            dst.write(blk)
      if partially_calculated_checksum.hexdigest() != expected_checksum:
         raise FileChangedWhileReadingError()
