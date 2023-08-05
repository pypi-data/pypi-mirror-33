-- schapp schema version 4, ABuS v8, v9, v10, v11

-- Metadata of a path at the time of last backup. Any change indicates the file content may have changed.
create table last_checksummed(
   path text not null,
   st_dev int not null,
   st_ino int not null,
   ctime float not null, -- change time, not birth time
   mtime float not null);
create unique index last_checksummed_pk on last_checksummed(path);

-- one entry for each path if changed (timestamp or checksum) since last backup
-- removed when backup is purged
create table content(
   run_name text not null,
   path text not null,
   timestamp float not null,
   checksum text not null);
create unique index content_pk on content(run_name, path);
create index content_path on content(path, run_name);

create table location(
   checksum text not null,
   is_compressed int not null,
   archive_dir text not null);
create unique index location_pk on location(checksum);
create index location_archivedir on location(archive_dir);

create table run(
   run_name text not null,
   archive_dir text not null);
create unique index completed_run_pk on run(run_name);

-- Files that are known not to exist any more because they were missing from the latest run.
-- These are not included in restore despite having backups.
-- Once the deletion is old enough, all backups of the file can be purged.
create table deletion(
   path text not null,
   timestamp float not null); -- time path was first detected deleted
create unique index deletion_pk on deletion(path);
