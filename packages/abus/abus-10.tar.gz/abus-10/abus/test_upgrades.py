# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import logging
import os
from abus.testbase import AbusTestBase
from abus import backup
from abus import database
from abus import main

class UpgradeTests(AbusTestBase):
   def upgrade_and_check_tables_and_columns(self):
      # creation of database object causes the upgrade:
      with database.connect(self.databasepath, self.archivedir):
         pass
      with self.get_direct_db_connection() as conn:
         schema= {t[0]: set(c[1] for c in conn.execute("PRAGMA table_info('{}')".format(*t)))
                  for t in conn.execute("select name from sqlite_master where type='table'")}
         expected_schema= {
            "run": {"run_name", "archive_dir"},
            "content": {"run_name", "path", "timestamp", "checksum"},
            "location": {"checksum", "archive_dir", "is_compressed"},
            "last_checksummed": {"path", "st_dev", "st_ino", "mtime", "ctime"},
            "deletion": {"path", "timestamp"},
            "_database_version": {"current_version"},
         }
         self.assertDictEqual(schema, expected_schema)

         tbl= conn.execute("select * from _database_version").fetchall()
         self.assertEqual(tbl, [("4",)])
      del conn # otherwise file handle does not get released for some reason

   def test_create(self):
      self.setup_directories()
      self.upgrade_and_check_tables_and_columns()

   def setup_old_db(self, create_schema_version: int) -> None:
      """Creates an old, empty DB schema for given version"""
      self.setup_directories()
      os.unlink(self.databasepath)
      schema_str= None
      with open("{}/upgrade-{}.sql".format(os.path.dirname(__file__), create_schema_version)) as stream:
         for line in stream:
            if schema_str is None:
               if line.strip()=="EOF":
                  schema_str= ""
            else:
               schema_str += line
      with self.get_direct_db_connection() as conn:
         conn.executescript(schema_str)
         if create_schema_version>=3:
            conn.execute("""create table _database_version(current_version text)""")
            conn.execute("""insert into  _database_version values('{}.0')""".format(create_schema_version))

   def test_upgrade_schema_2_to_3(self):
      """Tests the v2->v3 transition where some new data has to be generated from the contents of the
      archive directory, namely is_compressed."""
      for from_version in (1,2):
         with self.subTest(from_version=from_version):
            self.setup_old_db(from_version)
            with self.get_direct_db_connection() as conn:
               if from_version==1:
                  conn.executemany("insert into run(run_name, timestamp)values(?,?)",
                                   [("2017_10_27_0810", 56), ("2015_06_08_1200", None)])
                  conn.executemany("insert into location(checksum,archive_dir) values(?,?)",
                                   [("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "08/15"),
                                    ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "13/22")])
               else:
                  conn.execute("insert into completed_run(run_name) values(?)", ("2017_10_27_0810",))
                  conn.executemany("insert into content(run_name, path, timestamp, checksum) values(?,?,?,?)",
                                   [("2017_10_27_0810", "c:/some/path", 56, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
                                    ("2015_06_08_1200", "C:/bla/bla",   97, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
                                    ])
                  conn.executemany("insert into location(checksum,archive_dir) values(?,?)",
                                   [("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "08/15"),
                                    ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "13/22")])
            del conn # otherwise file handle does not get released for some reason
            # generates a few archive files:
            for f in ["/47/11/2017_10_27_0810.lst",
                      "/34/15/2015_06_08_1200.lst",
                      "/08/15/32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2",
                      "/13/22/f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa.z",
                     ]:
               abspath= self.archivedir+f
               os.makedirs(os.path.dirname(abspath), exist_ok=True)
               with open(abspath, "w"): pass
            self.upgrade_and_check_tables_and_columns()
            tbl= self.executesql("select run_name, archive_dir from run")
            self.assertEqual(set(tbl), {("2017_10_27_0810","47/11"),("2015_06_08_1200","34/15")})
            tbl= self.executesql("select checksum, is_compressed from location")
            self.assertEqual(set(tbl), {("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", 0),
                                        ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", 1),})

   def test_recover_from_upgrade_error(self):
      self.setup_old_db(2)
      with self.get_direct_db_connection() as conn:
         conn.execute("""drop table location""")
         conn.execute("""
            create table location(
               checksum text not null,
               archive_dir text not null)""")
         # introducing what after upgrade will be a unique constraint violation:
         conn.executemany("insert into location(checksum,archive_dir) values(?,?)",
                          [("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "08/15"),
                           ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "13/22"),
                           ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "13/22"),
                           ])
      checksum_before= backup.calculate_checksum(self.databasepath)
      with self.assertLogs() as logs:
         rc= main.main(["test", "-f", self.configfile, "-l"])
         self.assertEqual(rc, 4)
         self.assertTrue(any(r.levelno==logging.ERROR and "sqlite3.IntegrityError" in r.msg
                             for r in logs.records))
         self.assertTrue(any("index database upgrade failed, restoring backup" in r.msg
                             for r in logs.records))
      checksum_after= backup.calculate_checksum(self.databasepath)
      self.assertEqual(checksum_after, checksum_before)

   def test_upgrade_schema_3_to_4_checksum_cache_cleared(self):
      for from_version in range(1,4):
         with self.subTest(from_version=from_version):
            self.setup_old_db(from_version)
            with self.get_direct_db_connection() as conn:
               # old records must be deleted as part of the upgrade:
               conn.execute("insert into checksum_cache(dev, ino, timestamp, checksum) values(?,?,?,?)",
                            (23, 2**63-1, 1500000000, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"))
            self.upgrade_and_check_tables_and_columns()
            del conn # otherwise file handle does not get released for some reason

   def test_upgrade_schema_3_to_4_superfluous_content_rows(self):
      data= [
         ("c:/home/file_a", "2017_11_01_0001", 1500000000, "32b772"),
         ("c:/home/file_a", "2017_11_01_0002", 1500000000, "a9b773"),
         ("c:/home/file_a", "2017_11_01_0003", 1600000000, "a9b773"),
         ("c:/home/file_a", "2017_11_01_0004", 1500000000, "32b772"),
         ("c:/home/file_a", "2017_11_01_0005", 1600000000, "8971a4"),
         ("c:/home/file_a", "2017_11_01_0006", 1600000000, "8971a4"),
         ("c:/home/file_a", "2017_11_01_0007", 1600000000, "8971a4"),
         ("c:/home/file_a", "2017_11_01_0008", 1650000000, "f24873"),

         ("c:/home/file_b", "2017_11_01_0001", 1400000001, "321b772"),
         ("c:/home/file_b", "2017_11_01_0002", 1500000002, "a92b773"),
         ("c:/home/file_b", "2017_11_01_0003", 1600000003, "a93b773"),
         ("c:/home/file_b", "2017_11_01_0004", 1500000004, "324b772"),
         ("c:/home/file_b", "2017_11_01_0005", 1600000005, "89571a4"),
         ("c:/home/file_b", "2017_11_01_0006", 1600000006, "89671a4"),
         ("c:/home/file_b", "2017_11_01_0007", 1600000007, "89771a4"),
         ("c:/home/file_b", "2017_11_01_0008", 1650000008, "f284873"),

         ("c:/home/file_c", "2017_11_01_0008", 1650200008, "1355d0f"),

         ("c:/home/file_d", "2017_11_01_0001", 1650200008, "1355d0f"),
         ("c:/home/file_d", "2017_11_01_0003", 1650200008, "1355d0f"),
         ("c:/home/file_d", "2017_11_01_0005", 1650200008, "1355d0f"),
         ("c:/home/file_d", "2017_11_01_0006", 1650200008, "1355d0f"),
         ]
      expected_data= set()
      prev= (None, None, None)
      for p,r,t,c in data:
         if (p,t,c) != prev:
            expected_data.add((p,r,t,c))
            prev= (p,t,c)
      for from_version in range(1,4):
         with self.subTest(from_version=from_version):
            self.setup_old_db(from_version)
            with self.get_direct_db_connection() as conn:
               conn.executemany("insert into content(path, run_name, timestamp, checksum) values(?,?,?,?)", data)
            del conn # otherwise file handle does not get released for some reason
            self.upgrade_and_check_tables_and_columns()
            actual_data= self.executesql("select path, run_name, timestamp, checksum from content")
            self.assertEqual(set(actual_data), expected_data)
