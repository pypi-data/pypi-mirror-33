# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import time
from abus import config
from abus import main
from abus.testbase import AbusTestBase

def str2sec(s):
   return time.mktime(time.strptime(s, "%Y%m%d%H%M%S"))

class ConfigTester(AbusTestBase):
   def test_parse_date(self):
      now= str2sec("20170912150000")
      for d in range(1,9):
         for t in range(8):
            for future_date in True, False:
               for future_time in True, False:
                  d_str= "20171003" if future_date else "20170912"
                  t_str= "-160723" if future_time else "-130905"
                  test_str= d_str[-d:] + t_str[:t]

                  if d in (4,6,8) and t in (0,5,7):
                     expect_str= "2016"+d_str[-4:] if future_date and d==4 else d_str
                     expect_str += (t_str[1:t]+"000000")[:6]
                     try:
                        self.assertEqual(config._parse_date(test_str, now), str2sec(expect_str))
                     except:
                        print("test string:", test_str)
                        raise
                  else:
                     with self.assertRaises(ValueError):
                        print("test string:", test_str, "result:", config._parse_date(test_str, now))
      # TEST config: tomorrow 00:00 is not in the past
      self.assertEqual(config._parse_date("0913", now), str2sec("20170913000000"))
      # TEST config: any time strictly after tomorrow 00:00 is in the past
      self.assertEqual(config._parse_date("0913-000001", now), str2sec("20160913000001"))

   def test_parse_date_year_end(self):
      now= str2sec("20171231142536")
      # TEST config: 1 Jan 00:00 is tomorrow
      self.assertEqual(config._parse_date("0101", now), str2sec("20180101000000"))
      # TEST config: 1 Jan > 00:00 is in the past
      self.assertEqual(config._parse_date("0101-000001", now), str2sec("20170101000001"))

   def test_conflicting_cmdline_actions(self):
      self.setup_directories()
      # TEST config: action clash must be detected
      with self.assertRaisesRegex(config.ConfigurationError, "more than one command line action"):
         config.Configuration(["test", "-f", self.configfile, "--backup", "--restore"])
      # TEST config: action clash with implicit -l must be detected
      with self.assertRaisesRegex(config.ConfigurationError, "more than one command line action"):
         config.Configuration(["test", "-f", self.configfile, "--backup", "*.txt"])
      with self.assertRaisesRegex(config.ConfigurationError, "more than one command line action"):
         config.Configuration(["test", "-f", self.configfile, "--backup", "-a"])
      with self.assertRaisesRegex(config.ConfigurationError, "more than one command line action"):
         config.Configuration(["test", "-f", self.configfile, "--backup", "-d", "20170608"])

   def test_init_creates_directory(self):
      self.setup_directories()
      os.unlink(self.databasepath)
      os.rmdir(self.archivedir)
      rc= main.main(["test", "-f", self.configfile, "--init"])
      self.assertEqual(rc, 0)
      self.assertTrue(os.path.isfile(self.databasepath))
      # non-standard database file:
      db_path= self.otherdir+"/index_database"
      self.write_config_file("indexdb " +db_path)
      os.unlink(self.databasepath)
      os.rmdir(self.archivedir)
      rc= main.main(["test", "-f", self.configfile, "--init"])
      self.assertEqual(rc, 0)
      self.assertTrue(os.path.isfile(db_path))
      self.assertFalse(os.path.exists(self.databasepath))

   def test_retention_parsing(self):
      self.setup_directories()
      def get_cfg_for_retention(*retention_strings):
         self.write_config_file(*retention_strings)
         return config.Configuration(["test", "-f", self.configfile, "-l"])

      # default
      cfg= get_cfg_for_retention()
      self.assertEqual(cfg.retention, [(1,7), (56,150)])
      # std
      cfg= get_cfg_for_retention("retain 7 20  1 10  .25 2  28 182")
      self.assertEqual(cfg.retention, [(.25,2), (1,10), (7,20), (28,182)])
      # non-numbers
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 7 28  56 b")
      # missing arguments
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 7 28  14 56 28")
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain")
      # duplicates
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 1 10  7 10")
      # non-factors
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 4 10  7 20")

   def test_compressed_extensions(self):
      self.setup_directories()
      # TEST config: compressed_extensions must match the right files
      compressed_by_default= set("jpg jpeg tgz".split())
      compressed_by_option= set("jpg jpeg jpfg".split())
      never_compressed= set("txt jpe mp5".split())

      for use_default_list in (True, False):
         if not use_default_list:
            self.write_config_file("compressed_extensions mp[34] jp*g ZIP")
         cfg= config.Configuration(["test", "-f", self.configfile, "-l"])
         for ext in compressed_by_default | compressed_by_option | never_compressed:
            with self.subTest(ext=ext, use_default_list=use_default_list):
               expect_compressed= ext in (compressed_by_default if use_default_list else compressed_by_option)
               self.assertEqual(expect_compressed, cfg.is_already_compressed("c:\\dir\\file."+ext))
               self.assertEqual(expect_compressed, cfg.is_already_compressed("c:/dir/file."+ext))
               self.assertEqual(expect_compressed, cfg.is_already_compressed("c:/dir/file."+ext.upper()))

   def test_threads_arg_parsing(self):
      self.setup_directories()
      def go(config_line):
         self.write_config_file(config_line)
         return config.Configuration(["test", "-f", self.configfile, "-l"]).n_threads
      n_threads= go("")
      self.assertGreaterEqual(n_threads, 1)
      self.assertLessEqual(n_threads, 8)
      # TEST config: trailing spaces on threads option are ignored
      self.assertEqual(go("threads 3 "), 3)
      for bad_arg in ["3 2", "3.4"]:
         with self.assertRaises(config.ConfigurationError):
            go("threads "+bad_arg)
