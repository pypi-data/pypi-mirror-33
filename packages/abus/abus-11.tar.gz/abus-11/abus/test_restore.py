# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from   io import StringIO
import os
import sqlite3
import sys
from   typing import FrozenSet, Optional, Tuple
import unittest.mock
from abus import backup
from abus import crypto
from abus import database
from abus import main
from abus.testbase import AbusTestBase

class RestoreTests(AbusTestBase):
   def test_simple_restore(self):
      self.setup_backup_with_well_known_checksums()
      self.remove_dir_contents(self.restoredir)
      rc= main.main(["test", "-f", self.configfile, "-r"])
      self.assertEqual(rc, 0)
      self.assertEqual(sum(1 for _ in self.find_files(self.restoredir)), len(self.expected_backups))
      for path, archive_name in self.expected_backups:
         restore_path=  path.replace(self.homedir, self.restoredir)
         actual= backup.calculate_checksum(restore_path)
         expected= archive_name[:64]
         self.assertEqual(actual, expected)

   def test_restore_does_not_overwrite(self):
      self.setup_backup_with_well_known_checksums()
      self.remove_dir_contents(self.restoredir)
      pfx_len= len(self.homedir)+1
      expected_restore_dir_entries= [
         path[pfx_len:].partition("/")[0] for path,_ in self.expected_backups]
      for filename in expected_restore_dir_entries:
         with open(filename, "w", newline='\n') as f: f.write("Hello World\n")
      rc= main.main(["test", "-f", self.configfile, "-r"])
      self.assertEqual(rc, 0)
      for filename in expected_restore_dir_entries:
         actual= backup.calculate_checksum(filename)
         self.assertEqual(actual, "d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26")

   def test_no_partial_backupfile_is_left(self):
      self.setup_backup_with_well_known_checksums()
      path, archivename= max(self.expected_backups)
      expected_checksum= "42" # causes Exception which is expected not to leave file behind
      password= "Would you like to buy some air?"
      open_dst_function= crypto.open_lzma
      backup_path= self.archivedir+"/42"
      with self.assertRaises(backup.FileChangedWhileReadingError):
         backup.make_backup_copy(path, expected_checksum, backup_path, open_dst_function, password)
      self.assertFalse(os.path.exists(backup_path))
      self.assertFalse(os.path.exists(backup_path+".part"))
      # making doubly sure the file would normally have been created (the source path might just be wrong, for example):
      backup.make_backup_copy(path, archivename[:64], backup_path, open_dst_function, password)
      self.assertTrue(os.path.exists(backup_path))
      self.assertFalse(os.path.exists(backup_path+".part"))

   def test_allversions_restore(self):
      self.setup_multiple_backups()
      n_versions= sum(1 for direntry in self.find_files(self.archivedir)
                        if len(direntry.name) in(64,66))
      rc= main.main(["test", "-f", self.configfile, "-r", "-a"])
      self.assertEqual(rc, 0)
      self.find_files(self.restoredir)
      n_restored= sum(1 for _ in self.find_files(self.restoredir))
      self.assertEqual(n_restored, n_versions)

   def test_bug_index_error_if_no_files_match(self):
      self.setup_backup_with_well_known_checksums()
      self.remove_dir_contents(self.restoredir)
      rc= main.main(["test", "-f", self.configfile, "-r", self.homedir])
      self.assertEqual(rc, 0)
      self.assertEqual(list(self.find_files(self.restoredir)), [])

   def test_paths_from_different_drive(self):
      self.setup_backup_with_well_known_checksums()
      with sqlite3.connect(self.databasepath) as conn:
         conn.execute("""update content set path= replace(path, 'C:', 'E:') where path like '%/my_%'""")
      rc= main.main(["test", "-f", self.configfile, "-r"])
      self.assertEqual(rc, 0)
      files= list(self.find_files(self.restoredir))
      self.assertEqual(len(files), 4)

   def test_zerodivision(self):
      # bug: restore progress bar could try to divide by 0
      self.setup_backup_with_well_known_checksums()
      with unittest.mock.patch('time.time', side_effect=lambda: 1500000000):
         rc= main.main(["test", "-f", self.configfile, "-r"])
      self.assertEqual(rc, 0)
      files= list(self.find_files(self.restoredir))
      self.assertEqual(len(files), 4)

   def run_list(self, *params) -> str:
      """Runs abus -l and returns stdout"""
      orig_stdout= sys.stdout
      sys.stdout= StringIO()
      try:
         self.run_main("--list", *params)
         result= sys.stdout.getvalue()
      finally:
         sys.stdout= orig_stdout
      return result

   def test_backslash_at_list(self):
      self.setup_directories()
      path= self.homedir +"/6301/603578B040C4"
      path_with_backslash= self.homedir +"/6301\\603578B040C4"
      self.create_file(path, 23)
      self.create_file(path+".txt", 43)
      self.run_backup()
      # TEST list: must allow \ in glob
      result= self.run_list(path_with_backslash)
      self.assertTrue(result.strip().endswith(path))
      # TEST restore: must allow \ in glob
      # TEST restore: must allow restoring single file (rather than get "Cannot overwrite ." error)
      self.run_main("--restore", path_with_backslash)
      self.assertTrue(os.path.exists(os.path.basename(path)))

   def test_case_insensitive_globbing(self):
      self.setup_directories()
      path= self.homedir +"/CamelCaseFilename.txt"
      path_wrong_case= self.homedir.upper() +"/camelcasefilename.txt"
      self.create_file(path, 23)
      self.run_backup()
      # TEST list: globbing must be case-insensitive
      result= self.run_list(path_wrong_case)
      self.assertTrue(result.strip().endswith(path))
      # TEST restore: globbing must be case-insensitive
      self.run_main("--restore", path_wrong_case)
      self.assertTrue(os.path.exists(os.path.basename(path)))

DAY= 86400

class RestoreDatabaseGetArchiveTests(AbusTestBase):
   t0= None
   paths= None
   def setUp(self):
      if not self.t0:
         paths= self.homedir_abs("file_a.txt", "file_b.txt", "file_c.txt")
         changes= [             [           2,         None,            5],
                                [        None,           11,           -1],
                                [           3,            7,           13],
                                [        None,           11,         None],
                                [          17,         None,           -1],
                  ]
         self.setup_directories()
         self.__class__.paths= paths
         self.__class__.t0= self.setup_backups(paths, changes)

   def _fileidx(self, partial_path):
      return min(i for i,p in enumerate(self.paths) if partial_path in p)

   def _test_one(self, cutoff_date:Optional[float], show_all:bool, expect:FrozenSet[Tuple[str,int]]):
      with database.connect(self.databasepath, self.archivedir) as db:
         actual= {(p,t) for p,t,a,c,z in db.get_archive_contents([], cutoff_date, show_all)}
         expected= {
            (self.paths[i], self.t0 +change_no*DAY +i*100)
            for i, change_no in ((self._fileidx(partial_path), change_no) for partial_path, change_no in expect)
            }
         self.assertEqual(actual, expected)
         # with filter:
         actual= {(p,t) for p,t,a,c,z in db.get_archive_contents(["*_c.txt"], cutoff_date, show_all)}
         expected= {(p,t) for p,t in expected if "file_c" in p}
         self.assertEqual(actual, expected)

   def test_database_get_archive_no_cutoff_show_all(self):
      """Writes various rundata to DB and checks that Database returns the right listings.
      No actual restoring or backing-up takes place"""

      # TEST restore: no cutoff date, show_all must show all versions subject to filter
      # TEST restore: two versions with same content must only be listed once with latest timestamp
      self._test_one(cutoff_date=None, show_all=True, expect={
         ("file_a", 0),
         ("file_a", 2),
         ("file_a", 4),
         ("file_b", 2),
         ("file_b", 3),
         ("file_c", 0),
         ("file_c", 2),
      })

   def test_database_get_archive_with_cutoff_show_last(self):
      # TEST restore: with cutoff date, no show_all must show latest version before date even if it was backed up after cutoff date
      # TEST restore: with cutoff date, deleted file must not be listed
      cutoff= self.t0 +2*DAY +150 # after file_b version 7
      self._test_one(cutoff_date=cutoff, show_all=False, expect={
         ("file_a", 2),
         ("file_b", 2),
         ("file_c", 0), # no historic deletions are stored so the pre-deletion version is active
      })

   def test_database_get_archive_with_cutoff_show_all(self):
      # TEST restore: with cutoff date, show_all must show latest version before date even if it was backed up after cutoff date
      # TEST restore: two versions with same content must only be listed once with latest timestamp
      cutoff= self.t0 +3*DAY +150 # after file_b 2nd version 11
      self._test_one(cutoff_date=cutoff, show_all=True, expect={
         ("file_a", 0),
         ("file_a", 2),
         ("file_b", 2),
         ("file_b", 3),
         ("file_c", 0),
         ("file_c", 2),
      })

   def test_database_get_archive_no_cutoff_show_last(self):
      # TEST restore: no cutoff date, no show_all must show latest versions subject to filter
      # TEST restore: no cutoff date, deleted file must not be listed
      self._test_one(cutoff_date=None, show_all=False, expect={
         ("file_a", 4),
         ("file_b", 3),
      })
