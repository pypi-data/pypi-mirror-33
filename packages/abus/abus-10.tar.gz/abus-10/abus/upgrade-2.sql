-- upgrade *from* schema 2 to schema 4

-- using non-null default values for archive_dir and is_compresed, will be updated by special case in python
update location set is_compressed= 0;
insert into run(run_name, archive_dir)
   select distinct run_name, ''
   from content
   ;
delete from completed_run;

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

EOF
-- schema 2, ABuS v3, v4

-- _database_version table is missing in schema 2 databases

create table content(
   run_name text not null,
   path text not null,
   timestamp float not null,
   checksum text not null);
create unique index content_pk on content(run_name, path);

create table location(
   checksum text not null,
   archive_dir text not null);
create unique index location_pk on location(checksum);
create index location_archivedir on location(archive_dir);

create table checksum_cache(
   dev int not null,
   ino int not null,
   timestamp float not null,
   checksum text not null);
create unique index checksum_cache_pk on checksum_cache(dev, ino);

-- An entry in completed_run indicates that the run completed without errors
-- and that `content` contains a complete list of files for the run, even
-- if some of the files have been purged since.
create table completed_run(
   run_name text not null);
create unique index completed_run_pk on completed_run(run_name);
