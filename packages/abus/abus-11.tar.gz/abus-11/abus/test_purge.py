# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import time
from   typing import Tuple
from abus import database
from abus import main
from abus.testbase import AbusTestBase

DAY= 86400

class PurgeTests(AbusTestBase):
   def test_purge_e2e(self):
      self.setup_directories()
      def checkdb(expected):
         data= self.executesql("""
            select run_name, path, timestamp, content.checksum, location.is_compressed
            from content
               left join location on location.checksum = content.checksum""")
         data= {(r+".lst",p,t,c,z) for r,p,t,c,z in data}
         self.assertEqual(data, expected)
      def get_new_archive_files(*existing_filenames) -> Tuple[set,set,set]:
         """Returns all new backup files give the one expected to exist already.

         :return: (new run filenames, new compressed backup filenames, new uncompressed)
         """
         all_files= set(direntry.name for direntry in self.find_files(self.archivedir))
         content_file= {n for n in all_files if n.endswith(".gz")}
         relevant= all_files -set(existing_filenames) -{"index.sl3", elt(content_file)}
         runs= set(n for n in relevant if n.endswith(".lst"))
         compressed= set(n for n in relevant if n.endswith(".z"))
         uncompressed= relevant -runs -compressed
         return runs, compressed, uncompressed
      def elt(s):
         """returns the only element from set"""
         self.assertEqual(len(s), 1)
         for e in s: return e

      day= 86400
      path_a,path_b = self.homedir_abs("path_a.txt", "path_b.gz")
      # -11 -10    -9 -8   -7  -2  0    t relative to now in days
      #  r0      r2-7 r1 r3-7  r2 r3    runs
      #  a0  a1                         both a versions come into r2's >7days slot, a0 is purged in r2
      #  b0           b1                b1 is in different r2 slot, but is purged in r3
      with self.turn_back_the_time(11*day):
         t0= time.time()
         self.create_file(path_a, 23, t0)
         self.create_file(path_b, 11, t0)
         rc= main.main(["test", "-f", self.configfile, "--backup"])
         self.assertEqual(rc, 0)
      runs, compressed, uncompressed = get_new_archive_files() # -> file_a0, file_b0, run0
      file_a0= elt(compressed)
      file_b0= elt(uncompressed)
      run0= elt(runs)
      checkdb({(run0, path_a, t0, file_a0[:64], 1),
               (run0, path_b, t0, file_b0, 0),
               })

      with self.turn_back_the_time(8*day):
         ta1= time.time()-2*day
         tb1= time.time()
         self.create_file(path_a, 17, ta1)
         self.create_file(path_b, 59, tb1)
         rc= main.main(["test", "-f", self.configfile, "--backup"])
         self.assertEqual(rc, 0)
      runs, compressed, uncompressed = get_new_archive_files(run0, file_a0, file_b0) # -> run1, file_a1, file_b1
      file_a1= elt(compressed)
      file_b1= elt(uncompressed)
      run1= elt(runs)
      checkdb({(run0, path_a, t0, file_a0[:64], 1),
               (run0, path_b, t0, file_b0, 0),
               (run1, path_a, ta1, file_a1[:64], 1),
               (run1, path_b, tb1, file_b1, 0),
               })

      with self.turn_back_the_time(2*day):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      # file_a0 purged
      runs, compressed, uncompressed = get_new_archive_files(run0, file_b0, run1, file_a1, file_b1) # -> run2
      self.assertEqual(compressed, set())
      self.assertEqual(uncompressed, set())
      elt(runs) # run2
      checkdb({(run0, path_b, t0, file_b0, 0),
               (run1, path_a, ta1, file_a1[:64], 1),
               (run1, path_b, tb1, file_b1, 0),
               })

      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      # file_b0, run0, run2 purged
      runs, compressed, uncompressed = get_new_archive_files(run1, file_a1, file_b1) # -> run3
      self.assertEqual(compressed, set())
      self.assertEqual(uncompressed, set())
      elt(runs) # run3
      checkdb({(run1, path_a, ta1, file_a1[:64], 1),
               (run1, path_b, tb1, file_b1, 0),
               })

   def test_db_get_purgeable_backups(self):
      self.setup_directories()
      rounders= [(1, 3), (4, 9)]
      aged_based_data= [
         # rounders:    0   0   0    0    4    4    4  4  4    4    4    4    1   1    1    1    1    1    1 <-- matches era calculation below
         ("path_a", (1000,20  ,  10, 9.1, 8.9, 8.1, 7.9,   6,   5, 4.1, 3.9, 3.1, 2.9,1.9, 1.5, 1.1, 0.9, 0.4, 0.2)),
         ("file_b", (None,19.5)),
         ("file_c", (1001,30  ,None,None,None,None,None,None,None,None,None,None,None,2  )),
         ("file_1d",(1002,31)), # shared checksums
         ("file_2d",(1002,32)),
         ("file_1e",(1003,33)), # shared checksums
         ("file_2e",(1003,None,None,None,None,None,   8)),
      ]
      now= time.time()
      timestamp_lists= {path:[None if age is None else now-age*86400 for age in ages] for path,ages in aged_based_data}
      checksum_lists= {path:[None if t is None else path[-1] +("0"*64 +str(t))[-63:] for t in timestamps]
                       for path,timestamps in timestamp_lists.items()}
      # maps checksums to 3 periods defined by rounders. Period id is maximum number of slots in that period (depending on time of day)
      eras= {}
      for path in timestamp_lists:
         for i, checksum in enumerate(checksum_lists[path]):
            if not checksum: continue
            eras[checksum]= 1 if i<4 else 3 if i<12 else 4
      with database.connect(self.databasepath, self.archivedir) as db:
         runs= [time.strftime("%Y_%m_%d_%H%M", time.localtime(t+65)) for t in timestamp_lists["path_a"]]
         all_checksums= set()
         for path in timestamp_lists:
            for run_name, timestamp, checksum in zip(runs, timestamp_lists[path], checksum_lists[path]):
               if not timestamp: continue
               db.add_backup_entry(run_name, path, timestamp, checksum)
               all_checksums.add(checksum)
         for checksum in all_checksums:
               db.remember_archivedir(checksum, checksum[-2:], True)
         del all_checksums

         result= db.get_purgeable_backups(rounders)
         self.assertTrue(all(a==c[-2:] for c,a,p,t in result)) # correct checksum

         result_checksums= set(c for c,a,p,t in result)

         # the latest versions must never be purged
         latest= set(cl[-1] for cl in checksum_lists.values())
         self.assertEqual(latest & result_checksums, set())

         # file_a
         keep= set(checksum_lists["path_a"]) - result_checksums
         # grouping by era, there must be at most as many versions to keep as slots in era.
         # cannot check "one per slot" directly because slot boundaries depend on time of day
         keep_by_era= {era: set() for era in eras.values()}
         for checksum in keep:
            keep_by_era[eras[checksum]].add(checksum)
         for era in keep_by_era:
            with self.subTest(contents=keep_by_era[era]):
               self.assertLessEqual(len(keep_by_era[era]), era)

         # file_c - one backup in oldest slot is always kept
         purged= [c for c in result_checksums if c.startswith("c")]
         self.assertEqual(purged, [checksum_lists["file_c"][0]]) # 30 and 2 stay

         # file_?d - oldest gets deleted because both paths don't need it any more
         purged= [c for c in result_checksums if c.startswith("d")]
         self.assertEqual(purged, [checksum_lists["file_1d"][0]])
         self.assertEqual(purged, [checksum_lists["file_2d"][0]])

         # file_?e - no deletion because the other still needs it
         purged= [c for c in result_checksums if c.startswith("e")]
         self.assertEqual(purged, [])

   def test_current_run_does_not_get_purged(self):
      """With the change that files are not added to content if the they have not changed since
      the last run, that current run may actually be empty, but must not be deleted if it is."""
      self.setup_directories()
      path= self.homedir_abs("some_file.txt")
      self.create_file(path, 57)
      with self.turn_back_the_time(2*86400):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
         self.assertEqual(rc, 0)
      runs= self.executesql("select run_name from run")
      self.assertEqual(len(runs), 1)
      run0= runs[0]

      with self.turn_back_the_time(86400):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
         self.assertEqual(rc, 0)
      runs= self.executesql("select run_name from run")
      self.assertEqual(len(runs), 2)
      runs.remove(run0)
      run1= runs[0]

      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      runs= self.executesql("select run_name from run")
      self.assertEqual(len(runs), 2)
      runs.remove(run0)
      self.assertNotEqual(runs[0], run1)

   def test_purges_of_deleted_files(self):
      """
      when there is a backup in the oldest slot
      and the file is deleted
      and the deletion date maps to the oldest slot
      then there should not be any other backups
      and the oldest slot backup should be purged
      """
      self.setup_directories()
      file_a, file_b= self.homedir_abs("file_a", "file_b")
      with self.turn_back_the_time(160*DAY):
         self.create_file(file_a, 2)
         self.run_backup()
      with self.turn_back_the_time(159*DAY):
         os.unlink(file_a)
         t_b = self.create_file(file_b, 3)
         self.run_backup()
      self.run_backup()
      actual= set(self.executesql("select path, timestamp from content"))
      self.assertEqual(actual, {(file_b, t_b)})

   def test_non_deleted_files_dont_get_purged(self):
      """
      when there is a backup in the oldest slot
      but the file is not deleted
      then the oldest slot backup must not be purged
      """
      self.setup_directories()
      file_a, file_b= self.homedir_abs("file_a", "file_b")
      with self.turn_back_the_time(160*DAY):
         t_a = self.create_file(file_a, 2)
         self.run_backup()
      with self.turn_back_the_time(159*DAY):
         t_b = self.create_file(file_b, 3)
         self.run_backup()
      self.run_backup()
      actual= set(self.executesql("select path, timestamp from content"))
      self.assertEqual(actual, {(file_a,t_a), (file_b,t_b)})

   def test_deleted_file_only_last_backup_is_purged(self):
      """
      when there is a backup in the oldest slot
      and the file is deleted
      but the deletion date does not map to the oldest slot
      then the oldest slot backup must not be purged
      """
      self.setup_directories()
      file_a, file_b= self.homedir_abs("file_a", "file_b")
      with self.turn_back_the_time(160*DAY):
         t_a = self.create_file(file_a, 2)
         self.run_backup()
      with self.turn_back_the_time(50*DAY):
         os.unlink(file_a)
         t_b = self.create_file(file_b, 3)
         self.run_backup()
      self.run_backup()
      actual= set(self.executesql("select path, timestamp from content"))
      self.assertEqual(actual, {(file_a,t_a), (file_b,t_b)})

   def test_deletion_table_purge(self):
      """
      when the last backup of a path is purged
      then the deletion entry is also purged
      and checksum entry is also purged
      """
      self.setup_directories()
      file_a, file_b= self.homedir_abs("file_a", "file_b")
      with self.turn_back_the_time(160*DAY):
         self.create_file(file_a, 2)
         self.create_file(file_b, 3)
         self.run_backup()
      self.assertNotEqual(self.executesql("select * from last_checksummed where path=?",file_a), [])
      with self.turn_back_the_time(159*DAY):
         os.unlink(file_a)
         self.run_backup()
      with self.turn_back_the_time(50*DAY):
         os.unlink(file_b)
         self.run_backup()
      self.assertEqual(self.executesql("select path from deletion order by path"), [(file_a,), (file_b,)])
      self.run_backup()
      self.assertEqual(self.executesql("select path from deletion"), [(file_b,)])
      self.assertEqual(self.executesql("select * from last_checksummed where path=?",file_a), [])
