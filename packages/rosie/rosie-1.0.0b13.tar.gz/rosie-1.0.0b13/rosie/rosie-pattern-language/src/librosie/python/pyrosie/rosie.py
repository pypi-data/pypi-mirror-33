# coding: utf-8
#  -*- Mode: Python; -*-                                              
# 
#  rosie.py     An interface to librosie from Python 2.7 and 3.6
# 
#  © Copyright IBM Corporation 2016, 2017, 2018.
#  LICENSE: MIT License (https://opensource.org/licenses/mit-license.html)
#  AUTHOR: Jamie A. Jennings

# TODO:
#
# - format the rosie errors
# 

from __future__ import unicode_literals, print_function

import json
from . import internal
from .adapt23 import *

# -----------------------------------------------------------------------------
# Rosie-specific

def librosie_path():
    return internal._librosie_path

# -----------------------------------------------------------------------------
# 

class engine (object):

    '''
    A Rosie pattern matching engine is used to load/import RPL code
    (patterns) and to do matching.  Create as many engines as you need.
    '''

    def __init__(self):
        self._engine = internal.engine()
    
    # -----------------------------------------------------------------------------
    # Compile an expression
    # -----------------------------------------------------------------------------

    def compile(self, exp):
        pat, errs = self._engine.compile(bytes23(exp))
        if not pat:
            raise_rosie_error(errs)
        return rplx(exp, pat)

    # -----------------------------------------------------------------------------
    # Functions for matching and tracing (debugging)
    # -----------------------------------------------------------------------------

    def match(self, pattern, input, **kwargs):
        errs = None
        if isinstance(pattern, str) or isinstance(pattern, bytes):
            pattern = self.compile(pattern)
        else:
            raise TypeError('pattern not a string or bytes: ' + repr(pattern))
        return pattern.match(input, **kwargs)

    def fullmatch(self, pattern, input, **kwargs):
        errs = None
        if isinstance(pattern, str) or isinstance(pattern, bytes):
            pattern = self.compile(pattern)
        else:
            raise TypeError('pattern not a string or bytes: ' + repr(pattern))
        return pattern.fullmatch(input, **kwargs)

##
## Needs a librosie function for applying a macro ('find', in this case)
##
#     def search(self, pattern, input, **kwargs):
#         errs = None
#         if isinstance(pattern, str) or isinstance(pattern, bytes):
#             pattern = self.compile(pattern)
#         else:
#             raise TypeError('pattern not a string or bytes: ' + repr(pattern))
#         return pattern.match(input, **kwargs)
##
## Needs a librosie function for applying a macro ('findall', in this case)
##
#     def findall(self, pattern, input, **kwargs):
#         errs = None
#         if isinstance(pattern, str) or isinstance(pattern, bytes):
#             pattern = self.compile(pattern)
#         else:
#             raise TypeError('pattern not a string or bytes: ' + repr(pattern))
#         return pattern.match(input, **kwargs)


## Other python re functions:
## finditer, split, sub, subn, escape, purge, exception re.error


    def trace(self, pattern, input, **kwargs):
        errs = None
        if isinstance(pattern, str) or isinstance(pattern, bytes):
            pattern = self.compile(pattern)
        else:
            raise TypeError('pattern not a string or bytes: ' + repr(pattern))
        return pattern.trace(input, **kwargs)

    # -----------------------------------------------------------------------------
    # Functions for loading statements/blocks/packages into an engine
    # -----------------------------------------------------------------------------

    def load(self, src):
        _, pkgname, errs = self._engine.load(bytes23(src))
        if errs:
            raise_rosie_error(errs)
        return pkgname

    def loadfile(self, filename):
        _, pkgname, errs = self._engine.loadfile(bytes23(filename))
        if errs:
            raise_rosie_error(errs)
        return pkgname

    def import_package(self, pkgname, as_name=None):
        ok, actual_pkgname, errs = self._engine.import_pkg(pkgname, as_name)
        if errs:
            raise_rosie_error(errs)
        return actual_pkgname

    # -----------------------------------------------------------------------------
    # Functions for reading and modifying various engine settings
    # -----------------------------------------------------------------------------

    def config(self):
        return json.loads(self._engine.config())

    def libpath(self, libpath=None):
        return self. _engine.libpath(libpath)

    def alloc_limit(self, newlimit=None):
        return self._engine.alloc_limit(newlimit)

    def __del__(self):
        self._engine = None

# -----------------------------------------------------------------------------

def raise_rosie_error(errs):
    raise RuntimeError('RPL error:\n{}'.format(errs))

# -----------------------------------------------------------------------------

class rplx(object):    

    def __init__(self, exp, internal_rplx):
        self._exp = exp                                  # bytes or str
        self._internal_rplx = internal_rplx
            
    def pattern(self):
        return self._exp
    
    # TODO: support endpos
    def match(self, input, pos=0, endpos=None, **kwargs):
        encoder = kwargs['encoder'] if 'encoder' in kwargs else 'json'
        m, l, a, _, _ = self._internal_rplx.engine.match(self._internal_rplx,
                                                         bytes23(input),
                                                         pos,
                                                         bytes23(encoder))
        if m == False:
            return None
        match_value = m if 'encoder' in kwargs else json.loads(m)
        return {'match': match_value, 'leftover': l, 'abend': (a == 1)}

    # TODO: support endpos
    def fullmatch(self, input, pos=0, endpos=None, **kwargs):
        m = self.match(input, pos, endpos, **kwargs)
        if m and (m['leftover'] != 0): return m
        return None

#     def search(self, input, pos=0, endpos=None):
#     def findall(...):


    # TODO: support endpos
    def trace(self, input, pos=0, endpos=None, **kwargs):
        encoder = kwargs['encoder'] if 'encoder' in kwargs else 'json'
        matched, trace_data = self._internal_rplx.engine.trace(self._internal_rplx,
                                                               bytes23(input),
                                                               pos,
                                                               bytes23(encoder))
        trace_value = trace_data if 'encoder' in kwargs else json.loads(trace_data)
        return {'matched': matched, 'trace': trace_value}
    
# -----------------------------------------------------------------------------

# class match(object):

#     def __init__(self, rosie_match):
#         ...
#     def re:
#     def string:
#     def pos:
#     def endpos:

#     def start:
#     def end:
#     def span:
