# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import gzip
import os
import time
import unittest.mock
from abus import config
from abus import crypto
from abus import database
from abus import rebuild
from abus.testbase import AbusTestBase

DAY= 86400

class RebuildTests(AbusTestBase):
   def _get_database_contents(self):
      """
      reads DB into sets

      :return: set with completed_run, content, and location rows (distinguishable by their lengths)
      """
      queries= ["select run_name, archive_dir from run",
                "select run_name, path, timestamp, checksum from content",
                "select checksum, archive_dir, is_compressed from location",
                ]
      result= set()
      with self.get_direct_db_connection() as conn:
         for q in queries:
            result.update(conn.execute(q))
      return result

   def test_rebuild_e2e(self):
      self.setup_multiple_backups()
      before= self._get_database_contents()
      os.unlink(self.databasepath)
      with database.connect(self.databasepath, self.archivedir, allow_create=True):
         pass
      self.run_main("--rebuild-index")
      after= self._get_database_contents()
      self.assertEqual(after, before)

   def test_timestamp_string_gets_converted_properly(self):
      # timestamp stores as 1508532089.993785 if you let sqlite3 convert
      self.setup_directories()
      with database.connect(self.databasepath, self.archivedir) as db:
         db.rebuild_location_table([['bcf1a11', '00/00', 1]])
         db.rebuild_content("name", "00/00", [['bcf1a11', '1508532089.9937847', 'path']])
      t= self.executesql("select timestamp from content")
      self.assertEqual(len(t), 1)
      self.assertEqual(t[0][0], 1508532089.9937847)

   records= [
         ("good", "47/11"),
         ("good", "/home/somepath", 1507934953.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         ("good", "/home/other.path", 1507934453.0, "bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8"),
         ("incomplete", "47/11"),
         ("incomplete", "/home/somepath", 1290000000.0, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
         ("incomplete", "/home/path", 1290003000.0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         ("error", "47/11"),
         ("error", "/home/somepath", 1507934900.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         ("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "47/11", 1),
         ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "47/11", 1),
         ("bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8", "47/11", 0),
         ('498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f', '47/11', 0),
      ]
   def run_rebuild(self, records, expected_updates, expected_inserts, expected_deletes):
      """
      Performs a complete rebuild run, filling the database from the parameters first.
      The rebuild should always end up at the state described by self.records.

      :param records: records to for initialising database
      :type records: iterable
      :param expected_updates: number of changes to existing records
      :param expected_inserts: number of new records
      :param expected_deletes: number of removed records
      """
      self.setup_directories()
      d= self.archivedir + "/47/11"
      os.makedirs(d)
      with crypto.open_txt(d+"/incomplete.lst", "w", self.password) as f:
         print("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2 1290000000.0 /home/somepath", file=f)
         print("498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f 1290003000.0 /home/path", file=f)
      with crypto.open_txt(d+"/error.lst", "w", self.password) as f:
         print("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa 1507934900.0 /home/somepath", file=f)
         print("error 0 /home/other.path", file=f)
      with crypto.open_txt(d+"/good.lst", "w", self.password) as f:
         print("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa 1507934953.0 /home/somepath", file=f)
         print("bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8 1507934453.0 /home/other.path", file=f)
      with crypto.open_txt(d+"/32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2.z", "w", self.password) as f:
         f.write("data")
      with crypto.open_txt(d+"/f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa.z", "w", self.password) as f:
         f.write("data")
      with crypto.open_txt(d+"/bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8", "w", self.password) as f:
         f.write("compressed data")
      with crypto.open_txt(d+"/498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f", "w", self.password) as f:
         f.write("compressed data")
      with gzip.open(self.archivedir+"/good.gz", "wt") as f:
         print("47/11/32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2.z", file=f)
         print("47/11/f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa.z", file=f)
         print("47/11/incomplete.lst", file=f)
         print("47/11/error.lst", file=f)
         print("47/11/good.lst", file=f)
         print("good.gz", file=f)
         print("index.sl3", file=f)
      with self.get_direct_db_connection() as conn:
         run_records= set(rac for rac in records if len(rac)==2)
         conn.executemany("insert into run(run_name,archive_dir) values(?,?)", run_records)
         content_records= (t for t in records if len(t)==4)
         conn.executemany("insert into content(run_name, path, timestamp, checksum) values(?,?,?,?)", content_records)
         location_records= (t for t in records if len(t)==3)
         conn.executemany("insert into location(checksum, archive_dir, is_compressed) values(?,?,?)", location_records)
      cfg= config.Configuration(["test", "-f", self.configfile, "--rebuild-index"])
      updates, inserts, deletes = rebuild.rebuild_index_db(cfg)
      expected_db= set(self.records)
      actual= self._get_database_contents()
      self.assertEqual(actual, expected_db)
      self.assertEqual(updates, expected_updates)
      self.assertEqual(inserts, expected_inserts)
      self.assertEqual(deletes, expected_deletes)

   def test_rebuild_no_changes(self):
      r= self.records
      self.run_rebuild(r, 0,0,0)

   def test_rebuild_missing_record(self):
      for i in range(9):
         with self.subTest(i=i):
            r= self.records[:i] + self.records[i+1:]
            self.run_rebuild(r, 0, 1, 0)

   def test_rebuild_changed_record(self):
      changes= [
         (0, "good", "08/15"),
         (1, "good", "/home/somepath", 1111111111.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         (1, "good", "/home/somepath", 1507934953.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (2, "good", "/home/other.path", 1111111111.0, "bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8"),
         (2, "good", "/home/other.path", 1507934453.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (4, "incomplete", "/home/somepath", 1111111111.0, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
         (4, "incomplete", "/home/somepath", 1290000000.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (5, "incomplete", "/home/path", 1111111111.0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         (5, "incomplete", "/home/path", 1290003000.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (7, "error", "/home/somepath", 1111111111.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         (7, "error", "/home/somepath", 1507934953.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (8, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "08/15", 1),
         (8, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "47/11", 0),
         ]
      for iteration, change in enumerate(changes):
         with self.subTest(i=iteration):
            r= list(self.records)
            i= change[0]
            r[i]= change[1:]
            self.run_rebuild(r, 1, 0, 0)

   def test_rebuild_extra_location(self):
      r= self.records + [
            ("caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5", "08/15", 1),
         ]
      self.run_rebuild(r, 0,0,1)

   def test_rebuild_extra_entry(self):
      r= self.records + [
            ("good", "/home/completely.different", 1507934453.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         ]
      self.run_rebuild(r, 0,0,1)

   def test_rebuild_extra_run(self):
      r= self.records + [
            ("extra", "08/15", 1),
            ("extra", "/home/completely.different", 1507934453.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         ]
      self.run_rebuild(r, 0,0,2)

   def test_rebuild_spaces_in_filesname(self):
      self.setup_directories()
      d= self.archivedir + "/47/11"
      os.makedirs(d)
      with crypto.open_txt(d+"/32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2.z", "w", self.password) as f:
         f.write("data")
      with crypto.open_txt(d+"/498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f", "w", self.password) as f:
         f.write("data")
      with crypto.open_txt(d+"/2017_10_31_1232.lst", "w", self.password) as f:
         print("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2 1290000000.0 /home/sicko/hello world.txt", file=f)
         print("498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f 1290003000.0 /home/sicko/real  sick.txt", file=f)
      with gzip.open(self.archivedir+"/2017_10_31_1232.gz", "wt") as f:
         print("47/11/2017_10_31_1232.lst", file=f)
      self.run_main("--rebuild-index")
      self.assertEqual(self._get_database_contents(),
                       {('32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2', '47/11', 1),
                        ('498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f', '47/11', 0),
                        ("2017_10_31_1232", "47/11"),
                        ("2017_10_31_1232", "/home/sicko/hello world.txt", 1290000000.0, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2" ),
                        ("2017_10_31_1232", "/home/sicko/real  sick.txt",  1290003000.0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f")})

   def test_rebuild_from_old_files_does_not_cause_superfluous_entries(self):
      """
      When rebuilding database
      and runfiles contain repeated entries because they are from abus<=7
      then rebuilt content table should not contain repeated entries
      """
      self.setup_directories()
      backup_dir= self.archivedir+"/00"
      os.makedirs(backup_dir)
      with crypto.open_txt(backup_dir+"/2017_07_14_1200.lst", "w", self.password) as f:
         print("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2 1500000100.0 /home/change_ts.txt", file=f)
         print("498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f 1500000200.0 /home/change_sum_and_ts.txt", file=f)
         print("caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5 1500000300.0 /home/change_neither.txt", file=f)
      with crypto.open_txt(backup_dir+"/2017_07_15_1200.lst", "w", self.password) as f:
         print("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2 1500100100.0 /home/change_ts.txt", file=f)
         print("bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8 1500100200.0 /home/change_sum_and_ts.txt", file=f)
         print("caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5 1500000300.0 /home/change_neither.txt", file=f)
      with crypto.open_txt(backup_dir+"/2017_07_16_1200.lst", "w", self.password) as f:
         print("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2 1500100100.0 /home/change_ts.txt", file=f)
         print("bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8 1500100200.0 /home/change_sum_and_ts.txt", file=f)
         print("caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5 1500000300.0 /home/change_neither.txt", file=f)
      for b in ["32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f", "bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8", "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"]:
         with crypto.open_txt(backup_dir+"/"+b, "w", self.password) as f:
            f.write(b)
      with gzip.open(self.archivedir+"/2017_07_15_1200.gz", "wt") as f:
         print("00/32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", file=f)
         print("00/498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f", file=f)
         print("00/bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8", file=f)
         print("00/caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5", file=f)
         print("00/2017_07_14_1200.lst", file=f)
         print("00/2017_07_15_1200.lst", file=f)
         print("00/2017_07_16_1200.lst", file=f)
      self.run_main("--rebuild-index")
      expected= {
         ("2017_07_14_1200", "/home/change_ts.txt",         1500000100.0, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
         ("2017_07_14_1200", "/home/change_sum_and_ts.txt", 1500000200.0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         ("2017_07_14_1200", "/home/change_neither.txt",    1500000300.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         ("2017_07_15_1200", "/home/change_ts.txt",         1500100100.0, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
         ("2017_07_15_1200", "/home/change_sum_and_ts.txt", 1500100200.0, "bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8"),
      }
      actual= set(self.executesql("select run_name, path, timestamp, checksum from content"))
      self.assertEqual(actual, expected)

   def test_rebuild_clears_deletion_table(self):
      """
      when index db is rebuilt
      then the deletion table must be cleared (until it gets rebuilt properly)
      """
      self.setup_directories()
      backup_dir= self.archivedir+"/00"
      os.makedirs(backup_dir)
      path, path2 = self.homedir_abs("my_file.txt", "file_b.txt")
      def run_rebuilds(*expected_deleted_paths):
         expected_deletions= dict(self.executesql("select path, timestamp from deletion"))
         self.assertEqual(sorted(expected_deletions), sorted(expected_deleted_paths))
         def run_rebuild():
            self.run_main("--rebuild-index")
            actual= dict(self.executesql("select path, timestamp from deletion"))
            self.assertEqual(actual, expected_deletions)
         self.executesql("delete from deletion")
         run_rebuild()
         self.executesql("delete from deletion")
         self.executesql("insert into deletion(path,timestamp) values(?,?)", path, time.time())
         run_rebuild()
         self.executesql("delete from deletion")
         self.executesql("insert into deletion(path,timestamp) values(?,?)", path2, time.time())
         run_rebuild()

      # TEST all deletions must be cleared at the beginning of a rebuild
      with self.turn_back_the_time(13*DAY):
         self.create_file(path, 13)
         self.create_file(path2, 11)
         self.run_backup()
      run_rebuilds()

      # TEST a deletion must be rebuilt from the index file
      with self.turn_back_the_time(12*DAY):
         os.unlink(path)
         self.run_backup()
      if "debug - show index file contents":
         for direntry in self.find_files(self.archivedir):
            if direntry.name.endswith(".lst"):
               print(direntry.name+":")
               with crypto.open_txt(direntry.path, "r", self.password) as stream:
                  print(stream.read())
      run_rebuilds(path)

      # TEST a backup entry must clear a deletion at rebuild
      with self.turn_back_the_time(11*DAY):
         self.create_file(path, 7)
         self.run_backup()
      run_rebuilds()

      with self.turn_back_the_time(10*DAY):
         os.unlink(path)
         self.run_backup()
      run_rebuilds(path)

      # TEST a file-error entry must still clear a deletion at rebuild
      with self.turn_back_the_time(9*DAY):
         self.create_file(path, 5)
         with unittest.mock.patch('abus.backup.make_backup_copy', side_effect=RuntimeError):
            self.run_backup(expected_return_code=1)
      run_rebuilds()
