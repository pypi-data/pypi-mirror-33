#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import itertools

from anycsv.config import anycsvconfig as anycsvconfig
from pyjuhelpers.logging import log_func_detail

__author__ = 'jumbrich'

import structlog
log = structlog.get_logger()

from cchardet import UniversalDetector

def get_header_encoding(header):
    cont_type = None
    if 'Content-Type' in header:
        cont_type = header['Content-Type']
    elif 'content-type' in header:
        cont_type = header['content-type']

    header_encoding = None
    if cont_type and len(cont_type.split(';')) > 1:
        header_encoding = cont_type.split(';')[1]
        header_encoding = header_encoding.strip()
        if 'charset=' in header_encoding:
            header_encoding = header_encoding[8:]
        elif 'charset = ' in header_encoding:
            header_encoding = header_encoding[10:]
        elif 'charset =' in header_encoding:
            header_encoding = header_encoding[9:]
    return header_encoding


def detect_encoding_with_chardet(iostream, min_lines = 10, max_lines=anycsvconfig.NO_SNIFF_LINES):
    detector = UniversalDetector()

    if max_lines != -1:
        max_lines = max(min_lines, max_lines)

    c = 0
    for line in iostream:
        c += 1
        detector.feed(line)
        if c > min_lines and (detector.done or min(c, max_lines) == max_lines):
            break
    detector.close()
    return detector.result #{'encoding':, 'confidence':}

@log_func_detail(log, time_key="detect_encoding")
def detect_encoding(iostream, header=None,min_lines = 10, max_lines=anycsvconfig.NO_SNIFF_LINES):

    results = { 'default': {'encoding': anycsvconfig.DEFAULT_ENCODING} }

    results['lib_chardet'] = detect_encoding_with_chardet(iostream, min_lines,max_lines)

    if header:
        header_encoding = get_header_encoding(header)
        results['header'] = {'encoding': header_encoding}

    return results

def prob_encoding(ios, encoding_result, max_lines = anycsvconfig.NO_SNIFF_LINES ):

    cnt=b''
    for line in itertools.islice(ios, max_lines):
        cnt += line

    for k in anycsvconfig.ENC_PRIORITY:
        try:
            if k in encoding_result and encoding_result[k]['encoding'] is not None:
                content_encoded = cnt.decode(encoding=encoding_result[k]['encoding'])
                c_enc = encoding_result[k]['encoding']
                break
        except Exception as e:
            log.debug("Encoding Error",encoding_result[k]['encoding'])

    return c_enc
