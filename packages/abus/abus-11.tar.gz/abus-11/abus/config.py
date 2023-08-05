# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import argparse
from   fnmatch import fnmatch
import logging
import os
import psutil
import time
from   typing import Optional

class LogfileTracker(object):
   """Context manager for 0 or 1 logfile whose handlers will be removed properly"""
   def __init__(self):
      """Creates context manager for 0 or 1 logfile whose handlers will be removed properly"""
      self.handler= None
      logging.getLogger().setLevel(logging.DEBUG)
      self.formatter= logging.Formatter('%(asctime)s %(levelname)-7s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
   def open(self, path:str) -> None:
      """Opens logfile"""
      self.close()
      self.handler= logging.FileHandler(path, 'a', 'utf-8')
      self.handler.setFormatter(self.formatter)
      logging.getLogger().addHandler(self.handler)
   def have_logfile(self) -> bool:
      """whether the logfile path is known"""
      return self.handler is not None
   def close(self):
      """Closes logfile if one is open"""
      if self.handler:
         logging.getLogger().removeHandler(self.handler)
         self.handler.close()
      self.handler= None
   def __enter__(self):
      return self
   def __exit__(self, exc_type, exc_val, exc_tb):
      self.close()

class ConfigurationError(Exception):
   pass

class Configuration(object):
   """Combined backup configuration options from command line, environment, and config file"""
   ABUS_VERSION= 11
   def __init__(self, argv, logfile_tracker:LogfileTracker=None):
      """
      Combined backup configuration options from command line, environment, and config file (determined
      by command line or environment.

      :param argv: command line arguments (`sys.argv`).
      :param logfile_tracker: used for opening logfile once path is known
      """

      # Default values
      self.archive_root_path= None
      self.database_path= None
      self.logfile_path= None
      self.include= []
      self.exclude= []
      self.password= None
      self.minimum_size_for_compression= 4096
      self.compressed_extensions= "7z arj avi bz2 flac gif gz jar jpeg jpg lz lzmo lzo mov mp3 mp4 png rar tgz tif tiff wma xz zip".split()
      self.retention= [(1,7), (56,150)]
      self.n_threads= max(1, min(psutil.cpu_count()-1, 8))

      # Command line
      args= self._get_command_line_options(argv)
      self.is_backup= args.backup
      self.is_restore= args.restore
      self.is_init= args.init
      self.is_rebuild= args.rebuild_index
      self.list_all= args.a
      self.patterns= [p.replace("\\","/") for p in args.glob]
      self.cutoff= args.d
      self.is_list= args.list
      if not self.is_restore and (self.list_all or self.patterns or self.cutoff):
         self.is_list= True
      actions= self.is_list, self.is_backup, self.is_restore, self.is_init, self.is_rebuild
      n_actions= sum(1 for a in actions if a)
      if n_actions==0:
         return # will only report version, no config file necessary

      # Config file
      if args.f is not None:
         config_path= args.f
      elif "ABUS_CONFIG" in os.environ:
         config_path= os.environ["ABUS_CONFIG"]
      else:
         raise ConfigurationError("Missing config file path (-f option or ABUS_CONFIG environment variable)")
      with open(config_path, encoding="utf-8") as f:
         self._parse_config_file(f, logfile_tracker)

      if n_actions>1:
         if self.is_list and not args.list:
            raise ConfigurationError("more than one command line action (including implicit -l)")
         else:
            raise ConfigurationError("more than one command line action")
      if not self.archive_root_path:
         raise ConfigurationError("archive directory option not set")
      if not os.path.isdir(self.archive_root_path) and not self.is_init:
         raise ConfigurationError("missing archive directory ({})".format(self.archive_root_path))
      if not self.password:
         raise ConfigurationError("password option not set")
      if not self.include:
         raise ConfigurationError("missing or empty [include] section")
      if not self.logfile_path:
         raise ConfigurationError("logfile path option not set")

      if not self.database_path:
         self.database_path= self.archive_root_path+"/index.sl3"

   def _parse_config_file(self, lines, logfile_tracker:LogfileTracker):
      self.include= []
      self.exclude= []
      section= None
      for line in lines:
         line= line.strip()
         if not line or line.startswith('#'):
            pass
         elif line.lower().startswith("[incl"):
            section= self.include
         elif line.lower().startswith("[excl"):
            section= self.exclude
         elif line.lower().startswith("["):
            raise ConfigurationError("unknown section name: "+line)
         elif section is not None:
            line= line.replace("\\", "/")
            if line.endswith("/"): line= line[:-1]
            section.append(line)
         else:
            splut= line.split(maxsplit=1)
            if len(splut)!=2:
               raise ConfigurationError("missing value: "+line)
            keyword, args = splut
            if keyword=="archive":
               self.archive_root_path= args
            elif keyword=="compressed_extensions":
               self.compressed_extensions= args.split()
            elif keyword=="indexdb":
               self.database_path= args
            elif keyword=="logfile":
               self.logfile_path= args
               # Initialising log file now because it might be possible despite a subsequent
               # error during parsing.
               if logfile_tracker:
                  logfile_tracker.open(self.logfile_path)
            elif keyword=="password":
               self.password= args
            elif keyword=="retain":
               self.retention= _parse_retention_args(args)
            elif keyword=="threads":
               self.n_threads= _parse_threads_args(args)
            else:
               raise ConfigurationError("unknown option: "+keyword)

   @staticmethod
   def _get_command_line_options(argv):
      parser= argparse.ArgumentParser(
         prog=os.path.basename(argv[0]),
         description="""
            The Abingdon BackUp Script makes copies of files to a backup location on a local filesystem.
            For documentation, read the accompanying README or the project front page on PyPi.
            """,
         epilog="""Without any arguments, ABuS simply prints its version.
            If no action (init, rebuild-index, backup, list, restore) is specified
            then any other list/restore argument implies --list.""",
         )
      parser.add_argument('-f',
         action='store',
         metavar='path',
         help="""Path to config file required for defining backup location etc.
                 Defaults to value of the ABUS_CONFIG environment variable.""")
      parser.add_argument('--init',
         action='store_true',
         help='Creates an empty index database and the backup directory.')
      parser.add_argument('--rebuild-index',
         action='store_true',
         help="""Reconstructs the index database from static backup files. N.B.: You must convince yourself of the
            integrity of the content file <date>.gz first.""")
      parser.add_argument('--list', '-l',
         action='store_true',
         help='Lists the contens of the backup directory.')
      parser.add_argument('--backup',
         action='store_true',
         help="Backs up files to the backup directory.")
      parser.add_argument('--restore', '-r',
         action='store_true',
         help="Restores files from the backup directory to the current directory.")
      parser.add_argument('-a',
         action='store_true',
         help="""Includes all matching file versions when listing or restoring
            rather than only the latest matching version of each file.""")
      parser.add_argument('-d',
                          action='store',
                          type=_parse_date,
                          metavar="datetime",
                          help="""
            Cut-off time (format [[cc]yy]mmdd[-HHMM[SS]]) from which files are not included in listing or restore.
            The time defaults to midnight.
            The year defaults to the current year or the previous year if the date would be strictly after midnight tomorrow.
            Note that to show all files in May, say, the argument must be 0601.
            """)
      parser.add_argument('glob',
         nargs='*',
         help="Case-insensitive file path pattern (* matches /) of files to be included in listing or restore.")
      return parser.parse_args(argv[1:])

   def is_already_compressed(self, path:str) -> bool:
      """
      Returns whether the given file path's extension belongs to a compressed file format,
      meaning that the file's backup does not need to be compressed again.
      """
      ext= os.path.splitext(path)[-1]
      return any(fnmatch(ext, "."+p) for p in self.compressed_extensions)

   def mk_archive_path(self, archive_dir: str, filename:str, ext: Optional[str]= None) -> str:
      """
      Constructs an absolute path in the archive directory from subdirectory and filename.

      :param archive_dir: subdirectory of archive root or root itself if empty
      :param filename: filename relative to archive dir
      :param ext: will be appended to relpath if given
      """
      return (self.archive_root_path
              + ("/"+archive_dir if archive_dir else "")
              +"/" + filename
              + (ext if ext else "")
              )

def _parse_date(string, now=None):
   now_tuple= time.localtime(now)
   def convert(d_str, t_str, rel_year=0):
      full_t_str= t_str + "0"*(6-len(t_str))
      full_d_str= str(now_tuple.tm_year + rel_year)[:8-len(d_str)] + d_str
      return time.mktime(time.strptime(full_d_str + full_t_str, "%Y%m%d%H%M%S"))
   d_str, minus, t_str = string.partition("-")
   if (t_str=="") == (minus==""):
      if len(d_str) in(4,6,8) and len(t_str) in(0,4,6):
         if d_str.isdigit():
            if t_str=="" or t_str.isdigit():
               if len(d_str)==4:
                  rel_year= 1 if d_str=="0101" and now_tuple[1:3]==(12,31) else 0
                  t= convert(d_str, t_str, rel_year)
                  tomorrow= time.mktime(now_tuple[:3]+(0,0,0)+now_tuple[6:]) + 86400
                  if t > tomorrow:
                     t= convert(d_str, t_str, rel_year-1)
               else:
                  t= convert(d_str, t_str, 0)

               return t
   raise ValueError()

def _parse_retention_args(arg_string):
   try:
      values= tuple(float(a) for a in arg_string.split())
   except ValueError:
      raise ConfigurationError("expected numeric arguments: "+arg_string)
   n= len(values)
   if n==0 or n%2==1:
      raise ConfigurationError("expected pairs of numbers: "+arg_string)
   paired= ((values[i],values[i+1]) for i in range(0,n,2))
   retention= sorted(paired, key=lambda ra:ra[1])
   if len(set(age for _,age in retention)) < len(retention):
      raise ConfigurationError("duplicate retention age")
   rounders= [r for r,a in retention]
   for a,b in zip(rounders, rounders[1:]):
      if b % a != 0:
         raise ConfigurationError("retention frequencies {} and {} are not multiples".format(a,b))
   return retention

def _parse_threads_args(arg_string):
   try:
      value= int(arg_string)
   except ValueError:
      raise ConfigurationError("expected numeric argument for 'threads' option: "+arg_string)
   if value < 1:
      raise ConfigurationError("number of threads must be at least 1")
   return value
