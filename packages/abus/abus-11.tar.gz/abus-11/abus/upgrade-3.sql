-- upgrade *from* schema 3 to schema 4

-- v3->v4
delete from checksum_cache;

-- removing unnecessary entries from content, i.e. those that are the same as their predecessor
with CHAIN as(select content.path
            ,content.run_name
            ,max(PRED.run_name) as prev_run_name
         from content
            join content as PRED on PRED.path = content.path and PRED.run_name < content.run_name
         group by content.path, content.run_name
         )
      ,SUPERFLUOUS as (select content.rowid
         from content
            join CHAIN on CHAIN.path = content.path and CHAIN.run_name = content.run_name
            join content as PRED on PRED.path = CHAIN.path and PRED.run_name = CHAIN.prev_run_name
         where content.timestamp = PRED.timestamp and content.checksum = PRED.checksum
         )
   delete from content
   where rowid in(select rowid from SUPERFLUOUS)
   ;

-- obsolete columns
update run set is_complete= null;

EOF
-- schema 3, ABuS v5 v6 v7

-- one entry for each file that was present at a run, except if its backup had an error.
-- entry stays when backup is purged until whole run is purged
create table content(
   run_name text not null,
   path text not null,
   timestamp float not null,
   checksum text not null);
create unique index content_pk on content(run_name, path);
create index content_path on content(path);

create table location(
   checksum text not null,
   is_compressed int not null,
   archive_dir text not null);
create unique index location_pk on location(checksum);
create index location_archivedir on location(archive_dir);

create table checksum_cache(
   dev int not null,
   ino int not null,
   timestamp float not null,
   checksum text not null);
create unique index checksum_cache_pk on checksum_cache(dev, ino);

create table run(
   run_name text not null,
   archive_dir text not null,
   is_complete int not null);
create unique index completed_run_pk on run(run_name);
