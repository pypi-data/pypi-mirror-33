# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from abc import abstractmethod
from typing import Iterable, Tuple

class DatabaseRebuildMixin(object):
   def rebuild_location_table(self, actual_content_list: Iterable[Tuple[str, str, bool]]) -> Tuple[int, int, int]:
      """
      Adjusts the location table to reflect data in dictionary.

      :param actual_content_list: (checksum, archive_dir, is_compressed)s of required state
      :type actual_content_list: iterable
      :returns: counts: (updates, inserts, deletes)
      """
      actual_content= {checksum:(archive_dir,is_compressed)
                       for checksum,archive_dir,is_compressed in actual_content_list}
      updates= []
      deletes= []
      with self._get_connection() as conn:
         conn.execute("delete from deletion")
         for checksum,archive_dir,is_compressed in conn.execute("select checksum, archive_dir, is_compressed from location"):
            # leaving actual_content with all records that are not in database:
            actual_values= actual_content.get(checksum)
            if actual_values is None:
               deletes.append((checksum,))
            else:
               del actual_content[checksum]
               if actual_values!=(archive_dir,is_compressed!=0):
                  archive_dir, is_compressed= actual_values
                  updates.append((archive_dir, is_compressed, checksum))
         conn.executemany("delete from location where checksum = ?", deletes)
         conn.executemany("update location set archive_dir= ?, is_compressed= ? where checksum = ?", updates)
         data= ((k,a,b) for k,(a,b) in actual_content.items())
         conn.executemany("insert into location(checksum,archive_dir,is_compressed) values(?,?,?)", data)
      return len(updates), len(actual_content), len(deletes)

   def rebuild_content(self, run_name:str, run_archive_dir:str,
                       checksum_timestamp_path_rows: Iterable[Tuple[str,str,str]]) -> Tuple[int,int,int]:
      """
      Replaces all rows in content table for a given run_name with the given values.
      All calls from a single rebuild must be in order of run_name.

      :param run_name:Run whose content rows will all be deleted and then replaced.
      :param run_archive_dir: The relative dir containing the run file
      :param checksum_timestamp_path_rows: (checksum, timestamp, path)s - new rows without run_nam column.
         The checksum value may take special values 'error' or 'deleted' as per index file format.
      :return: number of records changed, added, deleted
      """
      typed_ctp= ((c,float(t),p) for c,t,p in checksum_timestamp_path_rows)
      with self._get_connection() as conn:
         conn.execute("""create temp table if not exists required_content(
            path text not null primary key,
            timestamp float not null,
            checksum text not null)""")
         conn.execute("delete from required_content")
         conn.executemany("insert into required_content(checksum, timestamp, path) values(?,?,?)", typed_ctp)
         conn.execute("""delete from deletion 
            where path in(select path from required_content where checksum<>'deleted')""")
         conn.execute("delete from required_content where checksum='error'")
         conn.execute("""insert into deletion(path, timestamp)
            select path, timestamp from required_content where checksum='deleted'""")
         conn.execute("delete from required_content where checksum='deleted'")
         conn.execute("delete from required_content where checksum not in(select checksum from location)")
         conn.execute("""delete from required_content 
            where rowid in(select required_content.rowid 
               from (select path, max(run_name) as prev_run 
                     from content
                     where run_name < ? 
                     group by path
                     ) as LATEST
                  join content on content.run_name = LATEST.prev_run and content.path = LATEST.path
                  join required_content on required_content.path = content.path 
                     and required_content.checksum = content.checksum 
                     and required_content.timestamp = content.timestamp)""", [run_name])
         changed= conn.execute("""select count(*)
            from content join required_content on content.path=required_content.path
               and (content.checksum!=required_content.checksum or content.timestamp!=required_content.timestamp)
            where content.run_name=?""", [run_name]).fetchall()[0][0]
         new= conn.execute("""select count(*)
            from required_content left join content on content.path=required_content.path and content.run_name=?
            where content.path is null""", [run_name]).fetchall()[0][0]
         removed= conn.execute("""select count(*)
            from content left join required_content on required_content.path = content.path
            where content.run_name=? and required_content.path is null""", [run_name]).fetchall()[0][0]
         conn.execute("delete from content where run_name=?", [run_name])
         conn.execute("""insert into content(run_name, path, timestamp, checksum)
            select ?, path, timestamp, checksum from required_content""", [run_name])
         exists= conn.execute("select archive_dir from run where run_name=?", [run_name]).fetchall()
         if len(exists)==0:
            new += 1
            conn.execute("""insert into run(run_name, archive_dir) values(?,?)""",
                         (run_name, run_archive_dir))
         elif exists[0]!=(run_archive_dir,):
            changed += 1
            conn.execute("""update run set archive_dir= ? where run_name=?""",
                         (run_archive_dir, run_name))
      return changed, new, removed

   def remove_runs(self, other_than: Iterable[str]):
      """
      Removes all runs from content and completed_runs, whose run_name is not in `other_than`

      :return: number of deleted rows
      """
      other_than= list(other_than)
      place_holders= ",?" * len(other_than)
      n= 0
      with self._get_connection() as conn:
         for table in "run", "content":
            stmt= "delete from "+table+" where run_name not in("+place_holders[1:]+")"
            cur= conn.execute(stmt, other_than)
            n += cur.rowcount
      return n

   @abstractmethod
   def _get_connection(self):
      raise NotImplementedError()
