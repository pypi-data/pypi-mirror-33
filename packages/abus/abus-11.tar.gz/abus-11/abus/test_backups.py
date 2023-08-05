# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import gzip
import os
import psutil
import shutil
import sqlite3
import time
import unittest.mock
from abus import backup
from abus import config
from abus import database
from abus import crypto
from abus import main
from abus import purge
from abus.testbase import AbusTestBase

class BackedUpHomedirTests(AbusTestBase):
   def test_simple_end_to_end_backup(self):
      self.setup_backup_with_well_known_checksums()

      # checking archive contents matches DB
      subdir,run_name = self.executesql("select archive_dir, run_name from run")[0]
      index_file_path_rel= subdir+"/"+run_name+".lst"
      expected_backupfiles= {"index.sl3", index_file_path_rel, run_name+".gz"}
      entries= self.executesql("""
         select path, archive_dir, location.checksum, is_compressed
         from content
            join location on location.checksum = content.checksum""")
      expected_backupfiles.update(a+"/"+c+(".z" if z else "") for p,a,c,z in entries)
      expected_backupfiles_abs= {self.archivedir+"/"+rel for rel in expected_backupfiles}
      actual= set(direntry.path.replace("\\","/")
                  for direntry in self.find_files(self.archivedir))
      self.assertEqual(actual, expected_backupfiles_abs)

      # checking archive contents matches what has been backed up
      # rs= e.g. ('C:/tmp/abushome/my_little_file', '40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880', 0)
      from_db= {(p, c+".z" if z else c) for p,a,c,z in entries}
      from_test= set(self.expected_backups)
      self.assertEqual(from_db, from_test)

      # checking that index files matches
      with crypto.open_txt(self.archivedir+"/"+index_file_path_rel, "r", self.password) as f:
         index_entries= set(l.strip() for l in f)
      dbentries= set("{} {} {}".format(*row)
                     for row in self.executesql("select checksum, timestamp, path from content"))
      self.assertEqual(index_entries, dbentries)

      # checking that contents file matches
      with gzip.open(self.archivedir+"/"+run_name+".gz", "rt", encoding="UTF-8") as stream:
         lines= {l.strip() for l in stream}
      self.assertEqual(lines, expected_backupfiles)

      # decrypting backup
      my_litte_backup= [e for e in expected_backupfiles_abs if "/40aff2e" in e]
      self.assertEqual(len(my_litte_backup), 1)
      self.assertEqual(os.stat(my_litte_backup[0]).st_size, 256+80) # 80 for salt, init vector, and checksum
      with crypto.open_bin(my_litte_backup[0], "r", self.password) as f:
         blk= f.read(8192)
         self.assertEqual(len(blk), 256)
         self.assertEqual(blk, bytearray(range(256)))

   def test_error_is_written_to_runfile(self):
      self.setup_directories()
      path= self.homedir_abs("some_file.txt")
      self.create_file(path, 23)
      with unittest.mock.patch('abus.backup.make_backup_copy', side_effect=RuntimeError):
         self.run_backup(expected_return_code=1)
      rs= self.executesql("select run_name, archive_dir from run")
      self.assertEqual(len(rs), 1)
      run_name, archive_dir = rs[0]
      index_file_path= self.archivedir+"/"+rs[0][1]+"/"+rs[0][0]+".lst"
      with crypto.open_txt(index_file_path, "r", self.password) as stream:
         contents= set(stream)
      error_line= "error 0 {}\n".format(path)
      self.assertIn(error_line, contents)
      self.assertTrue(os.path.isfile(self.archivedir+"/"+run_name+".gz"))

   def test_deletions(self):
      self.setup_directories()
      def check_deletions(*expected):
         actual= set(path for (path,) in self.executesql("select path from deletion"))
         self.assertEqual(actual, set(expected))
      def check_index_file(expected_dict):
         """
         Checks that latest index file has exactly given entries

         :param expected_dict: path -> "deleted"/"error"/"checksum"
         """
         run_name, archive_dir = self.executesql("select run_name, archive_dir from run order by run_name desc limit 1")[0]
         index_file= self.archivedir+"/"+archive_dir+"/"+run_name+".lst"
         with crypto.open_txt(index_file, "r", self.password) as stream:
            actual= { words[2]: words[0] if len(words[0])<64 else "checksum"
                      for words in (line.split() for line in stream)
                    }
         self.assertEqual(actual, expected_dict)

      file_a, file_b, error_dir = self.homedir_abs("file_a", "file_b", "subdir")

      with self.turn_back_the_time(4*86400):
         self.create_file(file_a, 17)
         self.create_file(file_b, 27)
         self.run_backup()
      check_deletions()
      check_index_file({ file_a:"checksum", file_b:"checksum" })

      with self.turn_back_the_time(3*86400):
         os.unlink(file_a)
         self.run_backup()
      check_deletions(file_a)
      # TEST a deletion must be written to the index file:
      check_index_file({ file_a:"deleted" })

      with self.turn_back_the_time(2*86400):
         self.create_file(file_a, 97)
         os.unlink(file_b)
         self.run_backup()
      check_deletions(file_b)
      check_index_file({ file_a:"checksum", file_b:"deleted" })

      # TEST an existing deletion's timestamp must not be updated
      # TEST an existing deletion must not be included in index file
      old_ts= self.executesql("select timestamp from deletion")
      self.assertEqual(len(old_ts), 1)
      with self.turn_back_the_time(1.5*86400):
         self.create_file(file_a, 13)
         self.run_backup()
      check_deletions(file_b)
      new_ts= self.executesql("select timestamp from deletion")
      self.assertEqual(new_ts, old_ts)
      check_index_file({ file_a:"checksum" })

      # when there is an error that risks not seeing some files
      # then files most not be marked deleted even if they are
      # but files that were seen must still be undeleted
      orig_scandir= os.scandir
      def mock_scandir(path):
         if path==error_dir:
            raise OSError("don't feel like reading that")
         return orig_scandir(path)
      with self.turn_back_the_time(86400):
         os.mkdir(error_dir)
         os.unlink(file_a)
         self.create_file(file_b, 73)
         with unittest.mock.patch("os.scandir", side_effect=mock_scandir):
            self.run_backup(expected_return_code=1)
      check_deletions()
      # a backup-error must prevent deletions from being written to the index file:
      check_index_file({ file_b:"checksum" })

      # when there is no error any more
      # then missing file must be marked as deleted
      self.run_backup()
      check_deletions(file_a)
      check_index_file({ file_a:"deleted" })

   def test_changing_file_gets_backed_up_after_retry(self):
      self.setup_directories()
      path= self.homedir_abs("some_file.txt")
      self.create_file(path, 23)
      # noinspection PyUnusedLocal
      def make_backup_copy_sideeffect(path, expected_checksum, backup_path, open_dst_function, password):
         self.create_file(path, 97) # 1244d0711c6534ee79a6d3b82cea33b76e766e46cbca75791ac9fa3a30e365f3
      with unittest.mock.patch('time.sleep'):
         with unittest.mock.patch('abus.backup.make_backup_copy',
                                  wraps=backup.make_backup_copy,
                                  side_effect=make_backup_copy_sideeffect):
            rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      rs= self.executesql("select run_name, archive_dir from run")
      self.assertEqual(len(rs), 1)
      rs= self.executesql("""select location.checksum
         from content join location on location.checksum = content.checksum""")
      self.assertEqual(len(rs), 1)
      self.assertEqual(rs[0][0], "1244d0711c6534ee79a6d3b82cea33b76e766e46cbca75791ac9fa3a30e365f3")

   def test_compressed_extensions_are_matched_case_insensitively(self):
      self.setup_directories()
      path= self.homedir_abs("IMG_0001.JPG")
      self.create_file(path, 26)
      # noinspection PyUnusedLocal
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      rs= self.executesql("""select location.checksum, location.is_compressed
         from content join location on location.checksum = content.checksum""")
      self.assertEqual(len(rs), 1)
      self.assertEqual(rs[0][0], "9941046094db30b12f5de992c403268a94cbdca3cf3eb7da20a8381404205a74")
      self.assertEqual(rs[0][1], 0)

   def test_always_changing_file_causes_error_after_5_attempts(self):
      self.setup_directories()
      primes= iter([17,19,23,29,31,37,41])
      path= self.homedir_abs("some_file.txt")
      self.create_file(path, next(primes))
      # noinspection PyUnusedLocal
      def make_backup_copy_sideeffect(path, expected_checksum, backup_path, open_dst_function, password):
         self.create_file(path, next(primes))
      with unittest.mock.patch('time.sleep'):
         with unittest.mock.patch('abus.backup.make_backup_copy',
                                  wraps=backup.make_backup_copy,
                                  side_effect=make_backup_copy_sideeffect) as mock:
            rc= main.main(["test", "-f", self.configfile, "--backup"])
            self.assertEqual(mock.call_count, 5)
      self.assertEqual(rc, 1)
      rs= self.executesql("select * from location")
      self.assertEqual(rs, [])

   def test_bad_include_entry_does_not_stop_other_backups(self):
      """bug: read error on c:/users/*/documents causes unhandled exception and aborts whole backup"""
      self.setup_directories()
      # Appending bad [include]-entry happens to run it first and used to prevent homedir from being backed up
      with open(self.configfile, "a") as stream:
         stream.write("C:/Users/*/Desktop\n")
      path= self.homedir_abs("some_file.txt")
      self.create_file(path, 23)
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 1)
      with self.get_direct_db_connection() as conn:
         rows= [conn.execute("select * from "+t).fetchall() for t in("content", "run", "location", "run")]
      self.assertEqual(len(rows[0]), 1)
      self.assertEqual(len(rows[1]), 1)
      self.assertEqual(len(rows[2]), 1)
      self.assertEqual(len(rows[3]), 1)

   def test_archive_dirs_to_use(self):
      def go(initial_usage: dict, expected_result: list):
         i= iter(backup.ArchiveDirsToUse._sequence(initial_usage))
         for archive_dir, n, skip in expected_result:
            actual= [next(i) for _ in range(n)]
            expect= [archive_dir]*n
            self.assertEqual(actual, expect)
            for _ in range(skip):
               next(i)
      go({},
         [("00", 100, 0), ("01", 100, 9800), ("00/01", 100, 0), ("01/01", 100, 9800), ("00/02", 100, 979800),
          ("99/99", 100, 0),
          ("00/00/01", 100, 0)])
      go({"00": 100, "45": 30},
         [("45", 70, 0), ("01", 100, 9700), ("00/01", 100, 0), ("01/01", 100, 9800), ("00/02", 100, 0)])

   def test_indexdb_in_different_location(self):
      self.setup_directories()
      path= self.homedir_abs("some_file.txt")
      self.create_file(path, 79)
      db_path= self.otherdir+"/index_database"
      shutil.move(self.databasepath, db_path)
      self.write_config_file("indexdb " +db_path)
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      with sqlite3.connect(db_path) as conn:
         content= conn.execute("select * from content").fetchall()
         subdir,run_name = conn.execute("select archive_dir, run_name from run").fetchall()[0]
      self.assertEqual(len(content), 1)
      self.assertFalse(os.path.exists(self.databasepath))

      content_file_path= self.archivedir+"/"+run_name+".gz"
      with gzip.open(content_file_path, "rt", encoding="UTF-8") as stream:
         lines= {l.strip() for l in stream}
      lines.remove(run_name+".gz")
      lines.remove(subdir+"/"+run_name+".lst")
      self.assertEqual(len(lines), 1)
      self.assertRegex(lines.pop(), "[a-z0-9]{64}")

      # bug: Exception in os.path.relpath if db on a different drive.
      os.unlink(content_file_path)
      cfg= config.Configuration(["test", "-f", self.configfile, "--backup"])
      with database.connect(cfg.database_path, cfg.archive_root_path, allow_create=False) as db:
         cfg.database_path= "X:/indexdb" # database_path no linger used, we can lie about it now
         with self.assertRaises(ValueError):
            os.path.relpath(cfg.database_path, cfg.archive_root_path)
         purge.write_content_file(cfg, db)

   def test_db_u64_ino_dev(self):
      self.setup_directories()
      path, st_dev, st_ino, mtime, ctime = "C:/tmp/some_file.txt", 2**63, 2**63, 1500000000.0, 0.0
      with database.connect(self.databasepath, self.archivedir) as db:
         db.remember_file_metadata(path, st_dev, st_ino, mtime, ctime)
         self.assertTrue(db.is_file_unchanged(path, st_dev, st_ino, mtime, ctime))

   def test_no_repeating_entries(self):
      self.setup_directories()
      day= 86400
      t0= round(time.time() - 6*day-1000)
      t1= t0 + 2*day

      file_a, file_b = self.homedir_abs("file_a.txt", "file_b.txt")
      self.create_file(file_a, 31, t0)
      with self.turn_back_the_time(6*day):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)

      self.create_file(file_a, 97, t1)
      with self.turn_back_the_time(4*day):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)

      self.create_file(file_a, 31, t0) # this should appear in the content
      with self.turn_back_the_time(2*day):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)

      os.rename(file_a, file_b)
      self.create_file(file_a, 31, t0) # this should not appear despite changed ino
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)

      entries= self.executesql("""select path, timestamp, checksum
         from content
         order by path, run_name""")
      expect= [
         (file_a, t0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         (file_a, t1, "1244d0711c6534ee79a6d3b82cea33b76e766e46cbca75791ac9fa3a30e365f3"),
         (file_a, t0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         (file_b, t0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         ]
      self.assertEqual(entries, expect)

   def test_lzma_memory_error(self):
      # bug: doing up to 20 simultaneous lzma compressions caused MemoryError on 32-bit Python.
      # Each lzma object requires 100MB.
      self.setup_directories()
      for fileno in range(20):
         source_path= self.homedir +"/large_file" +str(fileno)
         data= bytes(n*fileno%256 for n in range(1024*1024))
         with open(source_path,"wb") as f:
            for i in range(8):
               f.write(data)

      rc= main.main(["test", "-f", self.configfile, "--backup"])
      peak_memory= psutil.Process().memory_info().peak_wset
      self.assertEqual(0, rc)
      self.assertLess(peak_memory, 1000000000)
