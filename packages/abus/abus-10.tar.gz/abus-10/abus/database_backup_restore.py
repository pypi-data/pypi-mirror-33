# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from   abc import abstractmethod
import time
from   typing import Dict, Iterable, List, Optional, Set, Tuple

class DatabaseBackupRestoreMixin(object):
   def open_backup_run(self, archive_dir):
      time_tuple= time.localtime(time.time())
      # format chosen to make the run name a "word" in most editors:
      run_name= time.strftime("%Y_%m_%d_%H%M", time_tuple)
      with self._get_connection() as conn:
         n= conn.execute("select count(*) from run where run_name=?", [run_name]).fetchall()[0][0]
         if n>0:
            raise RuntimeError("There is already a run with the current timestamp (minute granularity")
         conn.execute("insert into run(run_name, archive_dir) values(?,?)", [run_name, archive_dir])
      return run_name

   def get_undeleted_files(self) -> Iterable[str]:
      """
      Returns paths of all files backed up that still existed at last run
      """
      with self._get_connection() as conn:
         rs= conn.execute("select distinct path from content where path not in(select path from deletion)")
         return (path for (path,) in rs)

   def get_archivedir_usage(self) -> Dict[str,int]:
      """
      Returns number of files in each known archive_dir as relpath -> n
      """
      with self._get_connection() as conn:
         rows= conn.execute("select archive_dir, count(*) as n from location group by archive_dir")
         counts= {archive_dir:n for archive_dir,n in rows}
         rows= conn.execute("select archive_dir, count(*) as n from run group by archive_dir")
         for archive_dir, n in rows:
            counts[archive_dir]= counts.get(archive_dir, 0) + n
         return counts

   def get_deletions(self) -> Iterable[str]:
      """
      Returns paths of all files currently marked deleted, i.e. files don't exist but previous backup still does.
      """
      with self._get_connection() as conn:
         return (path for (path,) in conn.execute("""select path from deletion"""))

   def is_file_unchanged(self, path: str, st_dev: int, st_ino: int, mtime: float, ctime: float) -> bool:
      """Whether the given path's metadata is unchanged since the last call to remember_latest_version,
      indicating that the file content is also unchanged and the file need not be backed up"""
      if st_dev>=2**63: st_dev -= 2**64 # sqlite cannot handle u64
      if st_ino>=2**63: st_ino -= 2**64
      with self._get_connection() as conn:
         rs= conn.execute("""select 1
            from last_checksummed
            where path=? and st_dev=? and st_ino=? and mtime=? and ctime=?""",
               (  path,      st_dev,      st_ino,      mtime,      ctime)).fetchall()
      return len(rs)==1

   def mark_deleted(self, timestamp:float, paths:Set[str]) -> None:
      """
      Marks files that no longer exist

      :param timestamp: time deletion has been detected (the closest we have to actual deletion time)
      :param paths: deleted files
      """
      with self._get_connection() as conn:
         conn.executemany("insert into deletion(path, timestamp) values(?,?)", ((p,timestamp) for p in paths))
         conn.executemany("delete from last_checksummed where path=?", ((p,) for p in paths))

   def unmark_deleted(self, path:str) -> None:
      """
      Ensures given path is not marked deleted as it has been seen to exist
      """
      with self._get_connection() as conn:
         conn.execute("delete from deletion where path=?", [path])

   def remember_file_metadata(self, path: str, st_dev: int, st_ino: int, mtime: float, ctime: float) -> None:
      """Stores metadata for path so that any change can be detected in future backups"""
      if st_dev>=2**63: st_dev -= 2**64 # sqlite cannot handle u64
      if st_ino>=2**63: st_ino -= 2**64
      with self._get_connection() as conn:
         cur= conn.execute("""
            update last_checksummed
            set st_dev=?, st_ino=?, mtime=?, ctime=? where path=?""",
               (st_dev,   st_ino,   mtime,   ctime,        path))
         if cur.rowcount==0:
            conn.execute("insert into last_checksummed(path, st_dev, st_ino, mtime, ctime) values(?,?,?,?,?)",
                                                      (path, st_dev, st_ino, mtime, ctime))

   def have_checksum(self, checksum: str) -> bool:
      """whether there is an existing backup for the given checksum"""
      with self._get_connection() as conn:
         rs= conn.execute("select archive_dir from location where checksum=?", [checksum]).fetchall()
      return len(rs)==1

   def remember_archivedir(self, checksum:str, archive_dir_rel:str, is_compressed:bool):
      """Records in database that a backup file has been created"""
      with self._get_connection() as conn:
         conn.execute("insert into location(checksum, archive_dir, is_compressed) values(?,?,?)",
                      (checksum, archive_dir_rel, is_compressed))

   def add_backup_entry(self, run_name: str, path: str, timestamp: float, checksum: str) -> bool:
      """Creates a new content entry unless the previous entry for the `path` has the same data.

      :returns: whether new entry was created"""
      with self._get_connection() as conn:
         prev= conn.execute("""select timestamp, checksum
            from content
            where path = ?
            order by run_name desc
            limit 1""", [path]).fetchall()
         if prev and prev == [(timestamp, checksum)]:
            return False
         conn.execute("""insert into content(run_name, path, timestamp, checksum)
            values(?,?,?,?)""", (run_name, path, timestamp, checksum))
         return True

   def get_all_backup_files(self) -> Iterable[Tuple[str,str,int]]:
      """
      Returns list of all checksums in backup

      :rtype: (checksum, archive_dir, is_compressed)s
      """
      with self._get_connection() as conn:
         return conn.execute("select checksum, archive_dir, is_compressed from location")

   def get_all_runs(self) -> Iterable[Tuple[str,str]]:
      """
      Returns list of all runs in DB

      :rtype: (run_name, archive_dir)s
      """
      with self._get_connection() as conn:
         return conn.execute("select run_name, archive_dir from run")


   def get_archive_contents(self, patterns:List[str], cutoff_date:Optional[float], show_all: bool) \
           -> Iterable[Tuple[str,float,str,str,int]]:
      """
      Returns content of archive for listing or restore.

      :param patterns: glob-operator patterns for path to match any of
      :param cutoff_date: time from which files are ignored or None
      :type cutoff_date: time.time() format
      :param show_all: whether all files should be returned rather than just those from the latest run
      :returns: (path, timestamp, archive_dir, checksum, is_compressed)s
      """
      with self._get_connection() as conn:
         where_clause= ""
         sql_parameters= []
         if cutoff_date is not None:
            where_clause += " and content.timestamp <= ?"
            sql_parameters.append(cutoff_date)
         if patterns:
            where_clause += " and (" + " or ".join("lower(content.path) glob ?" for _ in patterns) + ")"
            sql_parameters.extend(p.lower() for p in patterns)

         if show_all:
            sql= """
               with SELECTOR as(select content.path, content.checksum, max(content.timestamp) as timestamp
                     from content
                     where 1 {where_clauses}
                     group by content.path, content.checksum
                     )
                  select content.path, content.timestamp, location.archive_dir, location.checksum, location.is_compressed
                  from SELECTOR
                     join content on content.path = SELECTOR.path
                        and content.checksum = SELECTOR.checksum
                        and content.timestamp = SELECTOR.timestamp
                     join location on location.checksum = content.checksum
                  order by content.path, content.timestamp desc
               """.format(
                  where_clauses= where_clause,
                  )
         else:
            sql= """
               with SELECTOR as(select content.path, max(content.timestamp) as timestamp
                     from content
                     where 1 {where_clauses}
                     group by content.path
                     )
                  select content.path, content.timestamp, location.archive_dir, location.checksum, location.is_compressed
                  from SELECTOR
                     join content on content.path = SELECTOR.path and content.timestamp = SELECTOR.timestamp
                     join location on location.checksum = content.checksum
                     left join deletion on deletion.path = content.path {deletion_cutoff_clause}
                  where deletion.path is null
                  order by content.path, content.timestamp desc
               """.format(
                  where_clauses= where_clause,
                  deletion_cutoff_clause= "and deletion.timestamp <= ?" if cutoff_date else "",
                  )
            if cutoff_date:
               sql_parameters.append(cutoff_date)
         return conn.execute(sql, sql_parameters)

   @abstractmethod
   def _get_connection(self):
      raise NotImplementedError()
