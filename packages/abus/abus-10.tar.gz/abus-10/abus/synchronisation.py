# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import threading
from contextlib import contextmanager

_data_locks= {}
_datalocks_lock= threading.Lock()
_lock_pool= [] # I'm guessing that creating locks is expensive

@contextmanager
def global_data_lock(*data):
   """
   context manager for acquiring a lock specific to the given data
   :param data:
   :type data:
   :return:
   :rtype:
   """
   # _data_locks contains a threading.Lock and a reference count for each piece of data.
   # The reference count is required with the lock so that it can be deleted when no-one is using it,
   # so that _data_locks does not grow indefinetely.
   # The lock/count pair is implemented as a two-element list; it cannot be a tuple because it needs to be mutable
   # and an object would be overkill.
   with _datalocks_lock:
      if data in _data_locks:
         lock_and_count= _data_locks[data]
         lock_and_count[1] += 1
      else:
         lock= _lock_pool.pop() if _lock_pool else threading.Lock()
         lock_and_count= [lock, 1]
         _data_locks[data]= lock_and_count
   with lock_and_count[0]:
      yield
   with _datalocks_lock:
      if lock_and_count[1]==1:
         del _data_locks[data]
         _lock_pool.append(lock_and_count[0])
      else:
         lock_and_count[1] -= 1
