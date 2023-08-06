#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import logging
from collections import namedtuple
from pathlib import Path

from anycsv import exceptions
from pyjuhelpers.logging import log_func_detail

logger = logging.getLogger(__name__)
import os
import gzip

import requests
import io
import logging
from contextlib import closing

import structlog
log = structlog.get_logger()

@log_func_detail(log)
def getContentFromDisk(fname_csv, max_lines=-1):
    if not Path(fname_csv).exists():
        raise FileNotFoundError("File {} does not exist".format(fname_csv))

    if fname_csv[-3:] == '.gz':
        with gzip.open(fname_csv, 'rb') as f:
            if max_lines > -1:
                file_content = b''
                c =0
                for line in f:
                    file_content += line
                    c+=1
                    if c > max_lines:
                        break
            else:
                file_content = f.read()

    else:
        with io.open(fname_csv, 'rb') as f:
            if max_lines:
                file_content = b''
                #for line in f:
                    #print('l', type(line))
                #    break
                for line in f.readlines(max_lines):
                    #print ('l',type(line))
                    file_content += line
                    #print('l', type(file_content))
            else:
                file_content = f.read()

    return file_content

@log_func_detail(log)
def getContentAndHeaderFromWeb(url, max_lines=100):
    # save file to local directory

    headers= None
    content = None


    with closing(requests.get(url, timeout=1)) as r:
        r.raise_for_status()
        headers = r.headers
        if r.ok:

            if max_lines > - 1:
                input = r.iter_lines(chunk_size=64 * 1024)#, delimiter=b"\n")
                c = 0

                content = b''
                lines = []
                l = []
                for line in input:
                    content += line
                    lines.append(line)
                    l.append(len(line))
                    c += 1
                    if c >= max_lines:
                        break
                # print ('LINES', len(lines), 'SUM', sum(l))
                content = b'\n'.join(lines)
            else:
                content = r.read()

    return content, headers


ContentHeaderResult = namedtuple("ContentHeaderResult",['content', 'header', 'exception'])
def getContentAndHeader(csv=None,  max_lines=None)->ContentHeaderResult:

    content = None
    header = None
    exception=None

    try:
        import urllib
        if urllib.parse.urlparse(csv).scheme in ['http','https']:
            content, header, status_code = getContentAndHeaderFromWeb(csv, max_lines=max_lines)
        else:
            content = getContentFromDisk(csv, max_lines=max_lines)
    except Exception as e:
        log.debug("Exception ", csv=csv, exec=e.__class__.__name__, msg=str(e))
        exception = e
        status_code= 701

    return ContentHeaderResult(content, header,exception, status_code)


class TextIOBase(object):
    def __init__(self, ios, encoding):
        self.ios = ios
        self.encoding = encoding


    def __iter__(self):
        return self

    def __next__(self):
        return self.readline()

    def readline(self, *args, **kwargs):
        line = self.ios.readline()

        return line.decode(self.encoding)


class BufferedAutoEncodingStream(object):

    def __init__(self, csv, max_buffer=100, max_file_size=-1):

        self.hash = hashlib.md5()
        self.digest = None
        import urllib
        if urllib.parse.urlparse(csv).scheme in ['http', 'https']:
            resp = requests.get(csv, timeout=1)
            resp.raise_for_status()

            self.input = resp.iter_lines(chunk_size=64 * 1024)#, delimiter=b"\n")

        else:
            if not Path(csv).exists():
                raise FileNotFoundError("File {} does not exist".format(csv))

            if csv.endswith('.gz') or csv.endswith('.gzip'):
                ios = gzip.open(csv, 'rb')
            else:
                ios = io.open(csv, 'rb')
            self.input = ios

        self.max_file_size = max_file_size
        self.buffered_lines=[]
        self.lines_read = 0

        self.max_buffer_lines = max_buffer
        self.total_bytes_read=0

    @property
    def cur_buffer_size(self):
        return len(self.buffered_lines)

    @property
    def _buffer_full(self):
        return self.cur_buffer_size >= self.max_buffer_lines

    def reset(self):
        if self.lines_read > self.cur_buffer_size:
            raise IOError("Cannot reset buffer, more lines than buffer size read")
        self.lines_read = 0

    def __iter__(self):
        return self

    def readline(self):

        try:
            if self.lines_read >= self.cur_buffer_size:
                #we have more lines read as in buffer

                line = next(self.input)
                self.hash.update(line)

                self.total_bytes_read += len(line)

                if self.max_file_size>0 and self.total_bytes_read > self.max_file_size:
                    raise exceptions.FileSizeException(
                        "Maximum file size exceeded {} > {} ".format(self.total_bytes_read, self.max_file_size))

                if not self._buffer_full:
                    self.buffered_lines.append(line)
            else:
                line = self.buffered_lines[self.lines_read]

            self.lines_read +=1
            return line
        except StopIteration as e:
            self.digest = self.hash.hexdigest()
            raise e

    def __next__(self):
        try:
            return self.readline()
        except:
            raise StopIteration()

    def close(self):
        self.input.close()




if __name__ == '__main__':
    pass


