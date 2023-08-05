# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from   abc import abstractmethod
import time
from   typing import Iterable, List, Tuple

class DatabasePurgeMixin(object):
   def get_purgeable_backups(self, rounders:List[Tuple[float,float]]) -> List[Tuple[str,str,str,float]]:
      """
      Returns list of backup files that are superfluous and to be deleted.

      :param: rounders: retention policy definition: (rounder,age)s
      :return:  (checksum, archive_dir, path, timestamp)s
      """
      case_clause= "case " +"when timestamp >= ? then cast(timestamp/? as int)*? "*len(rounders) +"else 0 end"
      now= time.time()
      params= []
      for r,a in sorted(rounders):
         params.extend([now-a*86400, r*86400, r*86400])
      params.append(params[-3]) # slot 0 threshold for LONG_DELETED

      with self._get_connection() as conn:
         # SLOTTED sorts backups into groups from a similar time
         # KEEP_VERSIONS identifies latest in each slot as the one to keep
         # LONG_DELETED identifies paths that only have one very old backup _and_ have been deleted a long time ago;
         #              these are no longer kept despite being the latest version in their slot.
         cur= conn.execute("""
            with SLOTTED as(
                  select distinct path, timestamp, """+case_clause+""" as slot
                  from content
                  )
               ,LONG_DELETED as(
                  select deletion.path
                  from deletion
                     join SLOTTED on SLOTTED.path = deletion.path
                  where deletion.timestamp < ?
                  group by deletion.path
                  having count(SLOTTED.path)=1 and max(SLOTTED.slot)=0
                  )
               ,KEEP_VERSIONS as(
                  select path, max(timestamp) as timestamp
                  from SLOTTED
                  where path not in(select path from LONG_DELETED)
                  group by path, slot
                  )
               ,KEEP_CHECKSUMS as(
                  select distinct content.checksum
                  from content join KEEP_VERSIONS on content.path = KEEP_VERSIONS.path
                     and content.timestamp = KEEP_VERSIONS.timestamp
                  )
               ,PURGE as(
                  select distinct location.checksum, location.archive_dir, content.path, content.timestamp
                  from location
                     join content on content.checksum = location.checksum
                  where location.checksum not in(select checksum from KEEP_CHECKSUMS)
                  )
            select *
            from PURGE
            order by checksum, path, timestamp
            """, params)
         result= cur.fetchall()
      return result

   def remove_location_entry(self, checksum):
      """
      Reflects in DB that a backup file has been deleted

      :param checksum: of deleted location file
      """
      with self._get_connection() as conn:
         conn.execute("delete from content where checksum=?", [checksum])
         conn.execute("delete from deletion where path not in(select path from content)")
         conn.execute("delete from location where checksum=?", [checksum])

   def get_purgeable_runs(self) -> Iterable[Tuple[str,str]]:
      """
      Returns runs that can be purged.

      :returns: (run_name, archive_dir)s
      """
      with self._get_connection() as conn:
         return conn.execute("""
            select run_name, archive_dir
            from run
            where run_name not in(select run_name
                  from content join location on location.checksum = content.checksum) 
               and run_name <> (select max(run_name) from run)""") # TODO don't need join to location

   def purge_runs(self, run_names: Iterable[str]) -> None:
      """
      Purges given runs after checking that they can be purged.
      """
      # TODO don't need check, run file has already been purged
      run_names= set(run_names)
      run_names.intersection_update(r for r,a in self.get_purgeable_runs())
      run_names= list(run_names)
      if run_names:
         place_holders= ",?" * len(run_names)
         with self._get_connection() as conn:
            for table in ("run", "content"):
               conn.execute("delete from {} where run_name in({})".format(table, place_holders[1:]), run_names)

   @abstractmethod
   def _get_connection(self):
      raise NotImplementedError()
