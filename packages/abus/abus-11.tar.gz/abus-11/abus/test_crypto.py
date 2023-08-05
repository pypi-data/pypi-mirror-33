# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import unittest.mock
from abus import crypto
from abus.cornelib import partial_write_guard
from abus.testbase import AbusTestBase

class CryptoTester(AbusTestBase):
   def test_lzma_exception(self):
      # TEST crypto: if opening lzma or txt stream fails, underlying stream is still closed
      for tested_fun in (crypto.open_lzma, crypto.open_txt):
         with self.subTest(f=tested_fun):
            backup_path= self.archivedir+"/aabbccddeeff.z"
            with self.assertRaises(RuntimeError):
               with partial_write_guard(backup_path) as partial_path:
                  with unittest.mock.patch('lzma.open', side_effect=RuntimeError):
                     with tested_fun(partial_path, "w", self.password):
                        raise AssertionError("this cannot be executed")
                     raise AssertionError("nor this")
                  raise AssertionError("and this")
               raise AssertionError("and this again")
            self.assertFalse(os.path.isfile(partial_path))
            self.assertFalse(os.path.isfile(backup_path))
