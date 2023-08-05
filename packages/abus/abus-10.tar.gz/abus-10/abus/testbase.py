# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import itertools
import logging
import os
import shutil
import sqlite3
import time
from   typing import List, Optional, Union
import unittest
import unittest.mock

from abus import database
from abus import main

def get_tempdir():
   candidates_for_tmp= ["C:/tmp", "C:/temp"]
   if "TEMP" in os.environ: candidates_for_tmp.append(os.environ["TEMP"])
   for tempdir in candidates_for_tmp:
      if os.path.isdir(tempdir):
         return tempdir
   raise Exception("Could not find a temporary directory for tests")

class AbusTestBase(unittest.TestCase):
   password= "Sesam, öffne dich!"
   tempdir= get_tempdir()
   homedir= tempdir + "/abushome"
   otherdir= tempdir + "/abusother"
   archivedir= tempdir + "/abusarchive"
   restoredir= tempdir + "/abusrestore"

   @staticmethod
   def create_file(path:str, prime:int, timestamp:float=None) -> float:
      """Creates a file in the home directory

      :param prime: number that somehow determines the file content
      :param path: to create
      :param timestamp: mtime to touch file to, defaults time.time()
      :returns: timestamp of created file
      """
      os.makedirs(os.path.dirname(path), exist_ok=True)
      with open(path,"wb") as f:
         f.write(bytes(n*prime%256 for n in range(8192)))
      if timestamp is None:
         timestamp= time.time() # using the time that the test may have mocked
      os.utime(path, times=(timestamp,timestamp))
      return timestamp

   def homedir_abs(self, *rel_paths) -> Union[str, List[str]]:
      """Returns list of absolute paths from the home directory for the given relative paths.
      If a single path is given, the absolute path is returned directly rather than a list of 1."""
      result= [self.homedir +"/" + rel for rel in rel_paths]
      return result if len(result)!=1 else result[0]

   @property
   def databasepath(self):
      return self.archivedir+"/index.sl3"

   def executesql(self, sql, *params):
      """Runs sql statement on the index database and returns all rows.
      """
      with self.get_direct_db_connection() as conn:
         return conn.execute(sql, params).fetchall()

   @staticmethod
   def find_files(start):
      """Returns direntries for all files in `start`, recursively"""
      q= [start]
      while q:
         entries= list(os.scandir(q.pop())) # prevents iterator leakage
         yield from (e for e in entries if e.is_file())
         q.extend(e.path for e in entries if e.is_dir())

   def get_direct_db_connection(self):
      conn= sqlite3.connect(self.databasepath)
      conn.isolation_level= None # autocommit
      conn.execute("PRAGMA synchronous=OFF")
      return conn

   @staticmethod
   def remove_dir_contents(path):
      for direntry in os.scandir(path):
         if direntry.is_dir():
            shutil.rmtree(direntry.path)
         elif direntry.is_file():
            os.unlink(direntry.path)

   def setup_directories(self):
      """
      Sets up empty home, archive, and restore dirs, config file and empty database.

      :rtype: None
      """
      logging.basicConfig(level=logging.DEBUG)

      os.makedirs(self.homedir, exist_ok=True)
      os.makedirs(self.archivedir, exist_ok=True)
      os.makedirs(self.restoredir, exist_ok=True)
      os.makedirs(self.otherdir, exist_ok=True)
      os.chdir(self.restoredir)

      # empty them
      self.remove_dir_contents(self.homedir)
      self.remove_dir_contents(self.archivedir)
      self.remove_dir_contents(self.restoredir)
      self.remove_dir_contents(self.otherdir)

      self.configfile= self.otherdir + "/abusconfig.cfg"
      self.write_config_file()

      with database.connect(self.databasepath, self.archivedir, allow_create=True):
         pass

   def write_config_file(self, *extra_param_lines):
      with open(self.configfile, "w", encoding="utf-8") as f:
         print("logfile", self.otherdir + "/abuslog.txt", file=f)
         print("archive", self.archivedir, file=f)
         print("password", self.password, file=f)
         print("\n".join(extra_param_lines), file=f)
         print("[include]", file=f)
         print(self.homedir, file=f)

   def run_backup(self, expected_return_code:int=0) -> None:
      """
      Calls main() for backup with the config file and checks the return code.

      :param expected_return_code: asserts this is returned by main()
      """
      self.run_main("--backup", expected_return_code=expected_return_code)

   def run_main(self, *action_option: str, expected_return_code:int=0) -> None:
      """
      Calls main() with given action_option and the config file and checks the return code.

      :param action_option: E.g. --restore
      :param expected_return_code: asserts this is returned by main()
      """
      rc= main.main(("test", "-f", self.configfile) + action_option)
      self.assertEqual(rc, expected_return_code)

   def setup_backup_with_well_known_checksums(self):
      self.setup_directories()
      self.expected_backups= set() # contains (path rel to homedir, backup filename) pairs

      path= self.homedir_abs("my_valueable_file")
      with open(path, "w", encoding="utf-8") as f:
         for n in range(400):
            for p in range(10):
               print(n**p, file=f, end="")
            print(file=f)
      self.expected_backups.add((path,"73672933c00ab3cd730c8715a392ee6dee9ba2c0a8e5e5d07170b6544b0113ef.z"))

      path= self.homedir_abs("my_little_file")
      with open(path, "wb") as f:
         f.write(bytearray(range(256)))
      self.expected_backups.add((path,"40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880"))

      path= self.homedir_abs("subdir_a/I_am_in_a.tif")
      self.create_file(path, 31)
      self.expected_backups.add((path,"498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"))

      path= self.homedir_abs("subdir_b/I_am_in_b.bin")
      self.create_file(path, 97)
      self.expected_backups.add((path,"1244d0711c6534ee79a6d3b82cea33b76e766e46cbca75791ac9fa3a30e365f3.z"))

      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)

   def setup_multiple_backups(self):
      self.setup_directories()
      def primes():
         prev= [2]
         for c in itertools.count(3,2):
            for p in prev:
               if p*p>c:
                  yield c
                  prev.append(c)
                  break
               if c%p==0: break
      primes= primes().__iter__()

      all_paths= self.homedir_abs("a", "b", "s/a", "s/b", "t/a", "t/b")
      n= len(all_paths)*3//4
      for i in range(-3,0):
         subtract_time= -i*86400
         change_paths= all_paths if i==0 else all_paths[:n] if i==1 else all_paths[-n:]
         for path in change_paths:
            self.create_file(path, next(primes), time.time()-subtract_time-1200)
         with self.turn_back_the_time(subtract_time+600):
            rc= main.main(["test", "-f", self.configfile, "--backup"])
         self.assertEqual(rc, 0)

   @staticmethod
   def turn_back_the_time(seconds:float):
      """Returns a context manager for a mocked time.time() which is `seconds` behind the real time."""
      orig_time= time.time
      mock= lambda: orig_time() - seconds
      return unittest.mock.patch('time.time', side_effect=mock)

   def setup_backups(self, paths:List[str], changes:List[List[Optional[int]]]) -> float:
      """
      Sets up a series of backups from given data

      :param paths: absolute paths of all files involved in any of the backups
      :param changes: a "matrix" with a row per backup run and a column per element of `paths`. The value is

                      - *positive* to write the file, where the value is used as teh `prime` parameter for
                        create_home_file
                      - *negative* to delete the file
                      - *0 or None* to not touch the file at all.

      :return: Timestamp t0 chosen sufficiently far back for all runs to be in the past. Each action in `changes` is
               offset from t0 by adding 100s for each column and 86400s for each row. The times of the backup runs are
               approximately 100s after the last column.

      E.g.::

         changes = [
            [None, 7, 5],
            [   2, 3,-1],
         ]

      - paths[1] is set to content 7 at t0+100 (7 is the `prime` parameter for create_home_file)
      - paths[2] is set to content 5 at t0+200
      - backup run at t0+300
      - paths[0] is set to content 2 at t0+86400
      - paths[1] is set to content 3 at t0+86400+100
      - paths[2] is deleted at t0+86400+200
      - backup run at t0+86400+300
      """
      DAY= 86400
      n_changes= len(changes)
      n_files= len(paths)
      t0= round(time.time() - n_changes*DAY -DAY, -2)
      for change_no, change_list in enumerate(changes):
         for i, change in enumerate(change_list):
            if change:
               if change>0:
                  self.create_file(paths[i], change, t0 +change_no*DAY +i*100)
               else:
                  os.unlink(paths[i])
         with self.turn_back_the_time(time.time() - (t0 +change_no*DAY +n_files*100)):
            self.run_backup()
      return t0
