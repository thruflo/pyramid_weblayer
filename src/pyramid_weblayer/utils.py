#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides py:func`~pyramid_weblayer.utils.generate_hash`` utility function
  to generate seeded or random hashes.
"""

__all__ = [
    'generate_hash'
]

import hashlib
import random
import time

def generate_hash(s=None, algorithm='sha512', block_size=512):
    """ Generates a :py:func:`~hashlib.hash.hexdigest` string, either randomly
      or from a string or file like object (like an open file or a buffer).
      
      By default, the hash is randomly generated and uses the ``sha512``
      algorithm::
      
          >>> s1 = generate_hash()
          >>> isinstance(s1, str)
          True
          >>> len(s1) == 128
          True
          >>> s2 = generate_hash()
          >>> s1 == s2
          False
          >>> s3 = generate_hash(algorithm='sha512')
          >>> len(s1) == len(s3)
          True
      
      The hash can be generated from a seed::
      
          >>> generate_hash(s='a')
          '1f40fc92da241694750979ee6cf582f2d5d7d28e18335de05abc54d0560e0f5302860c652bf08d560252aa5e74210546f369fbbbce8c12cfc7957b2652fe9a75'
      
      Using ``None`` as the seed (which is the default) will, as we've seen, 
      generate a random value::
      
          >>> s6 = generate_hash(s=None)
          >>> s7 = generate_hash(s=None)
          >>> s6 == s7
          False
      
      Using a file like object (anything with a ``read()`` method) will use
      the contents of the file like object::
      
          >>> from io import BytesIO
          >>> sock = BytesIO()
          >>> s = b'abc'
          >>> l = sock.write(s)
          >>> l = sock.seek(0)
          >>> s8 = generate_hash(s=sock)
          >>> s9 = generate_hash(s=s)
          >>> s8 == s9
          True
      
      Reading the contents into memory in blocks of ``block_size``, which
      defaults to ``512``::
      
          >>> from mock import Mock
          >>> sock = Mock()
          >>> sock.read.return_value = None
          >>> s10 = generate_hash(s=sock)
          >>> sock.read.assert_called_with(512)
          >>> s10 = generate_hash(s=sock, block_size=1024)
          >>> sock.read.assert_called_with(1024)
      
      Using other types as a seed will raise a ``TypeError``::
      
          >>> generate_hash(s=[]) #doctest: +ELLIPSIS
          Traceback (most recent call last):
          ...
          TypeError: ...
      
      The algorithm name can also be passed in::
      
          >>> s4 = generate_hash(algorithm='md5')
          >>> s5 = generate_hash(algorithm='sha224')
          >>> len(s4) == 32 and len(s5) == 56
          True
      
      As long as it's available in :py:mod:`hashlib`::
      
          >>> generate_hash(algorithm='foo')
          Traceback (most recent call last):
          ...
          AttributeError: 'module' object has no attribute 'foo'
      
    """
    
    # get the hasher
    hasher = getattr(hashlib, algorithm)()
    # read in the data
    if hasattr(s, 'read') and callable(s.read):
        while True:
            data = s.read(block_size)
            if not data:
                break
            hasher.update(hasattr(data, 'encode') and data.encode() or data)
    else:
        if s is None:
            s = '%s%s' % (random.random(), time.time())
        if hasattr(s, 'encode') and callable(s.encode):
            hasher.update(s.encode())
        else:
            hasher.update(s)
    # return a hexdigest of the hash
    return hasher.hexdigest()
    

