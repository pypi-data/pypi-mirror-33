# -*- coding: UTF-8 -*-
# Copyright © 2017-2018 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import base64
from   contextlib import contextmanager
import lzma
import os

from cryptography.hazmat.primitives import ciphers, hmac, hashes
from cryptography.hazmat.primitives.kdf import pbkdf2
from cryptography.hazmat import backends

def _password_derive(key, salt):
   kdf = pbkdf2.PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=16,
      salt=salt,
      iterations=100000,
      backend=backends.default_backend()
   )
   return base64.urlsafe_b64encode(kdf.derive(key))

def string_split(s, at):
   """Returns s[:at], s[at:]"""
   return s[:at], s[at:]

class _WriteableEncryptedStream(object):
   """A write-only stream to an encrypted file. Data written to the stream is automatically encrypted."""
   def __init__(self, path, password):
      backend = backends.default_backend()
      str_key = password.encode()
      salt = os.urandom(16)
      hmac_salt = os.urandom(16)
      iv = os.urandom(16)
      key = _password_derive(str_key, salt)
      hmac_key = _password_derive(str_key, hmac_salt)
      self.checksummer = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
      cipher = ciphers.Cipher(ciphers.algorithms.AES(key), ciphers.modes.CTR(iv), backend=backend)
      self.cryptor = cipher.encryptor()
      initialiser= iv + salt + hmac_salt
      self.checksummer.update(initialiser)
      self.output_stream= open(path, mode="wb")
      self.output_stream.write(initialiser)
   def write(self, data):
      out = self.cryptor.update(data)
      self.checksummer.update(out)
      self.output_stream.write(out)
   def close(self):
      out = self.cryptor.finalize()
      self.checksummer.update(out)
      self.output_stream.write(out)
      signature = self.checksummer.finalize()
      self.output_stream.write(signature)
      self.output_stream.close()

class _ReadableEncryptedStream(object):
   """A read-only stream to an encrypted file. Data read from the stream is automatically decrypted."""
   def __init__(self, path, password):
      self.input_stream= open(path, "rb")
      str_key = password.encode()
      raw= self.input_stream.read(80)
      if len(raw)<80:
         raise RuntimeError("file too short")
      assert len(raw)==80
      initialiser= raw[:48]
      iv = initialiser[:16]
      salt = initialiser[16:32]
      hmac_salt = initialiser[32:48]

      # Bytes read from input_stream but not yet decrypted.
      # May or may not contain the signature at the end of file.
      # None indicates end of input_stream has been reached.
      self.read_ahead= raw[48:]

      # Decrypted from input_stream but not yet returned by read()
      self.decrypted= b""

      key = _password_derive(str_key, salt)
      hmac_key = _password_derive(str_key, hmac_salt)
      backend = backends.default_backend()
      cipher = ciphers.Cipher(ciphers.algorithms.AES(key), ciphers.modes.CTR(iv), backend=backend)
      self.cryptor = cipher.decryptor()
      self.checksummer = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
      self.checksummer.update(initialiser)
   def _fill(self, size):
      """Fills self.decrypted with sufficient data (unless end of file has been reached)"""
      if not self.read_ahead:
         return # end of stream has been reached
      bs= 8192 if size<0 else size
      while size==-1 or len(self.decrypted)<size:
         self.read_ahead += self.input_stream.read(bs)
         encrypted, self.read_ahead = string_split(self.read_ahead, -32)
         if len(encrypted) > 0:
            self.decrypted += self.cryptor.update(encrypted)
            self.checksummer.update(encrypted)
         else:
            # reached the end which means read_ahead is signature
            self.decrypted += self.cryptor.finalize()
            self.checksummer.verify(self.read_ahead)
            self.read_ahead= None
            break
   def read(self, size=-1):
      self._fill(size)
      data, self.decrypted = string_split(self.decrypted, size)
      return data
   @staticmethod
   def seekable():
      return False
   def close(self):
      self.input_stream.close()

@contextmanager
def open_bin(path, mode, password):
   if mode == "w":
      stream= _WriteableEncryptedStream(path, password)
   elif mode == "r":
      stream= _ReadableEncryptedStream(path, password)
   else:
      raise ValueError("Invalid mode: "+mode)
   try:
      yield stream
   finally:
      stream.close()

@contextmanager
def open_txt(path, mode, password):
   with open_bin(path, mode, password) as underlying:
      stream= lzma.open(underlying, mode + "t", encoding="UTF-8")
      try:
         yield stream
      finally:
         stream.close()

@contextmanager
def open_lzma(path, mode, password):
   """Opens an encrypted and compressed binary stream."""
   with open_bin(path, mode, password) as underlying:
      stream= lzma.open(underlying, mode + "b")
      try:
         yield stream
      finally:
         stream.close()
