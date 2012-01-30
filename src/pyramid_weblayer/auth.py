#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides two convienience functions to securely ``encrypt`` and ``verify``
  passwords::
  
      >>> cleartext_password = 'highly secure'
      >>> encrypted_password = encrypt(cleartext_password)
      >>> len(encrypted_password)
      119
      >>> verify('highly secure', encrypted_password)
      True
  
  Note that both functions normalise by stripping ``cleartext_password`` but
  don't do any case folding::
  
      >>> verify('Highly sEcuRe', encrypted_password)
      False
      >>> verify(' highly secure ', encrypted_password)
      True
      >>> verify('highly secure', encrypt(' highly secure '))
      True
  
  The ``verify`` function can be used as the compare function for a 
  `repoze.who`_ `SQLAuthenticatorPlugin`_, e.g. (in your paster.ini config)::
  
      who.plugin.sqlusers.compare_fn = pyramid_weblayer.auth.verify
  
  _`repoze.who`: http://docs.repoze.org/who/2.0/configuration.html
  _`SQLAuthenticatorPlugin`: http://docs.repoze.org/who/2.0/plugins.html
"""

__all__ = [
    'encrypt',
    'verify'
]

from passlib.apps import custom_app_context as pwd_context

def encrypt(cleartext_password, rounds=90000):
    """Ecrypt value ``rounds`` times.  The more rounds the more CPU cycles
      it takes.  The more CPU cycles, the slower and more secure it is.
    """
    
    value = cleartext_password.strip()
    return pwd_context.encrypt(value, scheme='sha512_crypt', rounds=rounds)

def verify(cleartext_password, encrypted_password):
    """Verify whether the passwords match."""
    
    value = cleartext_password.strip()
    return pwd_context.verify(value, encrypted_password)

