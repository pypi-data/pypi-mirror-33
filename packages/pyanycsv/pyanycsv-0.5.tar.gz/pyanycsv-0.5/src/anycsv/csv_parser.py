#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import csv as csvlib
import os
import logging
from collections import namedtuple

from anycsv import encoding
from anycsv.io_tools import BufferedAutoEncodingStream
from pyjuhelpers.logging import log_func_detail

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO



from anycsv.config import  anycsvconfig as anycsvconfig
from anycsv import encoding as E
from anycsv import dialect as D
from anycsv.csv_model import Table
from anycsv import io_tools
from anycsv import exceptions



import structlog
log = structlog.get_logger()


@log_func_detail(log, level=logging.DEBUG, time_key="csv.init_reader")
def reader(csv, skip_guess_encoding=anycsvconfig.SKIP_GUESS_ENCODING, delimiter=None, sniff_lines=anycsvconfig.NO_SNIFF_LINES, max_file_size=anycsvconfig.MAX_FILE_SIZE, encoding=anycsvconfig.DEFAULT_ENCODING):
    if not csv:
        raise exceptions.AnyCSVException('No CSV input specified')

    ios = BufferedAutoEncodingStream(csv, max_buffer=sniff_lines, max_file_size=max_file_size)

    if not skip_guess_encoding:
        encoding_result = E.detect_encoding(ios, min_lines=10, max_lines=sniff_lines)
        ios.reset()

        final_encoding = E.prob_encoding(ios, encoding_result, max_lines = sniff_lines )
        ios.reset()
    else:
        final_encoding = encoding

    dialect = D.guessDialect(ios, final_encoding)
    ios.reset()

    return Table(csv,ios, dialect, encoding=final_encoding)



class Table():

    def __init__(self, csv,ios, dialect, encoding):
        self.ios=ios
        self.csv=csv
        self.digest = None
        self.dialect = dialect
        self.encoding = encoding
        input = io_tools.TextIOBase(ios, encoding=encoding)
        self.reader = csvlib.reader(input, **dialect._asdict())

    def reset(self):
        self.ios.reset()
        input = io_tools.TextIOBase(self.ios, encoding=encoding)
        self.reader = csvlib.reader(input, **self.dialect._asdict())

    def __iter__(self):
        return self

    def __next__(self):
        try:
            row = next(self.reader)
            return row
        except Exception as e:
            self.digest = self.ios.digest
            self.total_bytes_read = self.ios.total_bytes_read

            raise e




#
#     table = Table(csv=csv)
#
#     table.dialect = meta['dialect']
#     if delimiter:
#         table.delimiter = delimiter
#         if 'delimiter' in table.dialect and table.dialect['delimiter'] != delimiter:
#             logger.warning('The given delimiter differs from the guessed delimiter: ' + dialect['delimiter'])
#     elif 'delimiter' in table.dialect:
#         table.delimiter = table.dialect['delimiter']
#     else:
#         raise exceptions.NoDelimiterException('No delimiter detected')
#
#     if 'quotechar' in table.dialect:
#         table.quotechar = table.dialect['quotechar']
#
#     table.encoding = meta['used_enc']
#
#     if content:
#         if max_file_size!=-1  and len(content)> max_file_size:
#             raise exceptions.FileSizeException("Maximum file size exceeded {} > {} ".format(len(content), max_file_size))
#         input = io.TextIOBase(content, encoding=table.encoding)
#     elif filename and os.path.exists(filename):
#         if filename[-3:] == '.gz':
#             if max_file_size != -1 and os.stat(filename).st_size/0.4 > max_file_size: #assuming 40% compression / com/orig=0.4 -> orig = com/0.4
#                 raise exceptions.FileSizeException(
#                     "Maximum file size exceeded {} > {} ".format(os.stat(filename).st_size, max_file_size))
#
#             input = io.TextIOWrapper(gzip.open(filename, 'r'), encoding=table.encoding)
#         else:
#             if max_file_size != -1 and os.stat(filename).st_size  > max_file_size:
#                 raise exceptions.FileSizeException(
#                     "Maximum file size exceeded {} > {} ".format(os.stat(filename).st_size, max_file_size))
#             input = io.open(filename,encoding=table.encoding)
#     elif url:
#         input = URLHandle(url,max_file_size,encoding=table.encoding)
#     else:
#         raise exceptions.AnyCSVException('No CSV input specified')
#
#
#
#
#
#
#     if table.encoding and ('utf-8' in table.encoding or 'utf8' in table.encoding):
#         table.csvReader = UnicodeReader(input,
#                                         delimiter=table.delimiter,
#                                         quotechar=table.quotechar)
#     else:
#         table.csvReader = EncodedCsvReader(input,
#                                      encoding=table.encoding,
#                                      delimiter=table.delimiter,
#                                      quotechar=table.quotechar)
#
#     return table
#
#
# def sniff_metadata(csv, skip_guess_encoding=config.SKIP_GUESS_ENCODING, sniff_lines=config.NO_SNIFF_LINES):
#
#
#     if not csv:
#         return {}
#
#     result = io_tools.getContentAndHeader(csv, max_lines = sniff_lines)
#     if result.exception is not None:
#         #something went seriously wrong -> abort
#         raise result.exception
#
#     meta = extract_csv_meta(header=result.header, content=result.content, skip_guess_encoding=skip_guess_encoding)
#
#     return meta
#
#
# CSVMeta = namedtuple("CSVMeta", ['used_encoding', 'dialect'])
# def extract_csv_meta(header, content=None, id='', skip_guess_encoding=False):
#     logger = logging.getLogger(__name__)
#     results = {'used_enc': None,
#                'dialect': {}}
#
#     # check if guess encoding is possible
#     if not skip_guess_encoding:
#         try:
#             import anycsv.encoding
#         except Exception as e:
#
#             print('Could not import "magic" library. To support encoding detection please install python-magic.')
#             skip_guess_encoding = True
#
#     # get encoding
#     if skip_guess_encoding:
#         results['used_enc'] = config.DEFAULT_ENCODING
#         content_encoded = content#.decode(encoding=results['used_enc'])
#         status="META encoding"
#     else:
#         results['enc'] = encoding.guessEncoding(content, header)
#
#         content_encoded = None
#         status="META "
#         c_enc = None
#         for k in config.ENC_PRIORITY:
#             #we try to use the different encodings
#             try:
#                 if k in results['enc'] and results['enc'][k]['encoding'] is not None:
#                     content_encoded = content.decode(encoding=results['enc'][k]['encoding'])
#                     c_enc = results['enc'][k]['encoding']
#                     status+=" encoding"
#                     break
#             except Exception as e:
#                 logger.debug('(%s) ERROR Tried %s encoding: %s', results['enc'][k]['encoding'],id, e)
#         if content_encoded:
#             results['used_enc'] = c_enc
#
#     # get dialect
#     try:
#         results['dialect'] = dialect.guessDialect(content_encoded)
#         status+=" dialect"
#     except Exception as e:
#         logger.warning('(%s)  %s',id, str(e))
#         results['dialect']={}
#
#     #if fName:
#     #    results['charset'] = encoding.get_charset(fName)
#
#     logger.debug("(%s) %s", id, status)
#     return results
#
#
# class URLHandle:
#     def __init__(self, url, max_file_size, encoding=None):
#         self.url = url
#         self.encoding = encoding
#         self._init()
#         self.max_file_size=max_file_size
#
#     def my_iter_lines(self,result):
#         buf = b''
#         for chunk in result.iter_content(chunk_size=64 * 1024):
#             buf += chunk
#             pos = 0
#             while True:
#                 eol = buf.find(b'\n', pos)
#                 if eol != -1:
#                     yield buf[pos:eol]
#                     pos = eol + 1
#                 else:
#                     buf = buf[pos:]
#                     break
#         if buf:
#             yield buf
#
#     def _init(self):
#         self._count = 0
#         req = requests.get(self.url)
#         #if self.encoding:
#         #self.input = req.iter_lines(chunk_size=1024, encoding=self.encoding   )
#         #else:
#         self.input = self.my_iter_lines(req)
#
#     def seek(self, offset):
#         if offset < self._count:
#             self._init()
#         while offset < self._count:
#             self.next()
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         _next = next(self.input)#.next()
#         self._count += len(_next)
#         if self.max_file_size != -1 and self._count > self.max_file_size:
#             raise exceptions.FileSizeException(
#                 "Maximum file size exceeded {} > {} ".format(self._count, self.max_file_size))
#
#         if self.encoding:
#             return _next.decode(self.encoding)
#         else:
#             return str(_next)
#
#     def next(self):
#         return self.__next__()
#
#
#
# class CsvReader:
#
#     def __init__(self, f, reader, encoding):
#         self.f = f
#         self.reader = reader
#         self.encoding = encoding
#         self._start_line = 0
#         self.line_num = 0
#
#     def __iter__(self):
#         return self
#
#     def seek_line(self, line_number):
#         if line_number < self.line_num:
#             self.f.seek(0)
#             self.line_num = 0
#         self._start_line = line_number
#
#     def _next(self):
#         while self._start_line > self.line_num:
#             next(self.reader)#.next()
#             self.line_num += 1
#         row = self.reader.__next__()
#         self.line_num += 1
#         return row
#
#
# class EncodedCsvReader(CsvReader):
#     def __init__(self, f, encoding="utf-8-sig", delimiter="\t", quotechar="'", **kwds):
#         if not quotechar:
#             quotechar = "'"
#         if not encoding:
#             encoding = 'utf-8-sig'
#         if not delimiter:
#             reader = csv.reader(f, quotechar=quotechar.encode('ascii'), **kwds)
#         else:
#             reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar,
#                                      **kwds)
#         CsvReader.__init__(self, f, reader, encoding)
#
#     def __next__(self):
#         row = self._next()
#         result = [str(s) for s in row]
#         return result
#
#     def next(self):
#         return self.__next__()
#
#
# class UnicodeReader(CsvReader):
#     def __init__(self, f, delimiter="\t", quotechar="'", encoding='utf-8', errors='strict', **kwds):
#         if not quotechar:
#             quotechar = "'"
#         if not encoding:
#             encoding = 'utf-8'
#         if not delimiter:
#             reader = csv.reader(f, quotechar=quotechar.encode('ascii'), **kwds)
#         else:
#             reader = csv.reader(f, delimiter=delimiter.encode('ascii'), quotechar=quotechar.encode('ascii'),
#                                      **kwds)
#         self.encoding_errors = errors
#         CsvReader.__init__(self, f, reader, encoding)
#
#     def next(self):
#         row = self._next()
#         encoding = self.encoding
#         encoding_errors = self.encoding_errors
#         float_ = float
#         unicode_ = str
#         return [(value if isinstance(value, float_) else
#                  unicode_(value, encoding, encoding_errors)) for value in row]


