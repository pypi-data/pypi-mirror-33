# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import logging
import os
import sys
import traceback

from abus import config
from abus import backup
from abus import database
from abus import purge
from abus import rebuild
from abus import restore

def main(argv):
   with config.LogfileTracker() as logfile_tracker:
      try:
         cfg= config.Configuration(argv, logfile_tracker)
         if cfg.is_backup:
            with database.connect(cfg.database_path, cfg.archive_root_path) as db:
               try:
                  backup.do_backup(cfg, db)
                  purge.do_purge(cfg, db)
               finally:
                  purge.write_content_file(cfg, db)
         elif cfg.is_list:
            restore.list_archive(cfg)
         elif cfg.is_restore:
            restore.restore(cfg)
         elif cfg.is_init:
            if os.path.exists(cfg.database_path):
               raise config.ConfigurationError(cfg.database_path+" exists already")
            os.makedirs(cfg.archive_root_path, exist_ok=True)
            with database.connect(cfg.database_path, cfg.archive_root_path, allow_create=True):
               print("created", cfg.database_path)
         elif cfg.is_rebuild:
            rebuild.rebuild_index_db(cfg)
         else:
            print("ABuS version", cfg.ABUS_VERSION)
      except config.ConfigurationError as e:
         error_message= str(e)
         rc= 2
      except RuntimeError as e:
         error_message= str(e)
         rc= 1
      except Exception as e:
         error_message= "".join(traceback.format_exception(type(e), e, e.__traceback__))
         rc= 4
      else:
         return 0

      print("Error:", error_message, file=sys.stderr)
      if logfile_tracker.have_logfile(): # tests that logging could be initialised before error occurred
         logging.error(error_message)

      return rc

