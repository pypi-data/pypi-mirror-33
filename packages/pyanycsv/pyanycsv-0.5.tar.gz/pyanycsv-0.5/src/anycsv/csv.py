#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals



"""
csv.py - read/write/investigate CSV files
"""


from _csv import Error, __version__, writer, reader, register_dialect, \
                 unregister_dialect, get_dialect, list_dialects, \
                 field_size_limit, \
                 QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE, \
                 __doc__
from _csv import Dialect as _Dialect

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Dialect:
    """Describe an Excel dialect.

    This must be subclassed (see csv.excel).  Valid attributes are:
    delimiter, quotechar, escapechar, doublequote, skipinitialspace,
    lineterminator, quoting.

    """
    _name = ""
    _valid = False
    # placeholders
    delimiter = None
    quotechar = None
    escapechar = None
    doublequote = None
    skipinitialspace = None
    lineterminator = None
    quoting = None

    def __init__(self):
        if self.__class__ != Dialect:
            self._valid = True
        self._validate()

    def _validate(self):
        try:
            _Dialect(self)
        except TypeError as e:
            # We do this for compatibility with py2.3
            raise Error(str(e))

class excel(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = str(',')
    quotechar = str('"')
    doublequote = True
    skipinitialspace = False
    lineterminator = str('\r\n')
    quoting = QUOTE_MINIMAL

register_dialect("excel", excel)

class excel_tab(excel):
    """Describe the usual properties of Excel-generated TAB-delimited files."""
    delimiter = str('\t')
register_dialect("excel-tab", excel_tab)



# Guard Sniffer's type checking against builds that exclude complex()
try:
    complex
except NameError:
    complex = float

class Sniffer:
    '''
    "Sniffs" the format of a CSV file (i.e. delimiter, quotechar)
    Returns a Dialect object.
    '''
    def __init__(self):
        # in case there is more than one possible delimiter
        self.preferred = [',', '\t', ';', ' ', ':']





