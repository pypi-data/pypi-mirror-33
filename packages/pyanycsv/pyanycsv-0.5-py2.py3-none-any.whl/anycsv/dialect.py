#!/usr/bin/python
# -*- coding: utf-8 -*-
import collections
import itertools
import re
from functools import reduce

from anycsv import csv
from pyjuhelpers.logging import log_func_detail

POSSIBLE_DELIMITERS = [',', '\t', ';', '#', ':', '|', '^']
preferred = [',', '\t', ';', ' ', ':']
from anycsv.config import anycsvconfig as anycsvconfig

import structlog
log = structlog.get_logger()

DialectTuple = collections.namedtuple("DialectTuple",[
        'delimiter',
        'doublequote',
        'lineterminator',
        'quotechar',
        'quoting',
        'skipinitialspace'])
@log_func_detail(log, time_key="guessDialect")
def guessDialect(ios, encoding='utf-8', max_lines=anycsvconfig.NO_SNIFF_LINES):
    c = 0

    cnt = b''
    for line in itertools.islice(ios, max_lines):
        cnt += line
    content_encoded = cnt.decode(encoding=encoding)

    dialect = sniff(content_encoded, POSSIBLE_DELIMITERS)

    if dialect is None:
        raise Exception('cannot guess dialect')

    return DialectTuple(**{
        'delimiter': dialect.delimiter,
        'doublequote': dialect.doublequote,
        'lineterminator': dialect.lineterminator,
        'quotechar': dialect.quotechar,
        'quoting': dialect.quoting,
        'skipinitialspace': dialect.skipinitialspace
    })


from _csv import Error, QUOTE_MINIMAL, Dialect


def sniff( sample, delimiters=None):
    """
    Returns a dialect (or None) corresponding to the sample
    """

    quotechar, doublequote, delimiter, skipinitialspace = _guess_quote_and_delimiter(sample, delimiters)
    delimiter1, skipinitialspace1 = _guess_delimiter(sample,delimiters)

    if delimiter is None and delimiter1:
        delimiter = delimiter1

    if delimiter:
        delimiter= delimiter.strip()
    if delimiter1:
        delimiter1= delimiter1.strip()

    if delimiter != delimiter1:
        #lets figure it out
        if len(delimiter) == 0 and len(delimiter1)!=0:
            delimiter=delimiter1


    if not delimiter:
        raise Error("Could not determine delimiter")

    class dialect(Dialect):
        _name = "sniffed"
        lineterminator = '\r\n'
        quoting = QUOTE_MINIMAL
        # escapechar = ''

    dialect.doublequote = doublequote
    dialect.delimiter = delimiter
    # _csv.reader won't accept a quotechar of ''
    dialect.quotechar = quotechar or '"'
    dialect.skipinitialspace = skipinitialspace

    return dialect


def _guess_quote_and_delimiter( data, delimiters):
    """
    Looks for text enclosed between two identical quotes
    (the probable quotechar) which are preceded and followed
    by the same character (the probable delimiter).
    For example:
                     ,'some text',
    The quote with the most wins, same with the delimiter.
    If there is no quotechar the delimiter can't be determined
    this way.
    """

    matches = []
    for restr in (
                  '(?P<delim>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?P=delim)', # ,".*?",
                  '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?P<delim>[^\w\n"\'])(?P<space> ?)',   #  ".*?",
                  '(?P<delim>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?:$|\n|\r\n)',  # ,".*?"
                  '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?:$|\n)'):                            #  ".*?" (no delim, no space)
        regexp = re.compile(restr, re.DOTALL | re.MULTILINE)
        m=regexp.findall(data)
        if len(m)>0:
            matches.append((m, regexp))
        #matches = regexp.findall(data)
        #if matches:
        #    break

    if not matches:
        # (quotechar, doublequote, delimiter, skipinitialspace)
        return ('', False, None, 0)
    quotes = {}
    delims = {}
    spaces = 0
    for ml, regexp in matches:
        for m in ml:
            n = regexp.groupindex['quote'] - 1
            key = m[n]
            if key:
                quotes[key] = quotes.get(key, 0) + 1
            try:
                n = regexp.groupindex['delim'] - 1
                key = m[n]
            except KeyError:
                continue
            if key and (delimiters is None or key in delimiters):
                delims[key] = delims.get(key, 0) + 1
            try:
                n = regexp.groupindex['space'] - 1
            except KeyError:
                continue
            if m[n]:
                spaces += 1

    quotechar = reduce(lambda a, b, quotes = quotes:
                       (quotes[a] > quotes[b]) and a or b, list(quotes.keys()))

    if delims:
        delim = reduce(lambda a, b, delims = delims:
                       (delims[a] > delims[b]) and a or b, list(delims.keys()))
        skipinitialspace = delims[delim] == spaces
        if delim == '\n': # most likely a file with a single column
            delim = ''
    else:
        # there is *no* delimiter, it's a single column of quoted data
        delim = ''
        skipinitialspace = 0

    # if we see an extra quote between delimiters, we've got a
    # double quoted format
    dq_regexp = re.compile(
                           r"((%(delim)s)|^)\W*%(quote)s[^%(delim)s\n]*%(quote)s[^%(delim)s\n]*%(quote)s\W*((%(delim)s)|$)" % \
                           {'delim':re.escape(delim), 'quote':quotechar}, re.MULTILINE)



    if dq_regexp.search(data):
        doublequote = True
    else:
        doublequote = False

    return (quotechar, doublequote, delim, skipinitialspace)


def _guess_delimiter( data, delimiters):
    """
    The delimiter /should/ occur the same number of times on
    each row. However, due to malformed data, it may not. We don't want
    an all or nothing approach, so we allow for small variations in this
    number.
      1) build a table of the frequency of each character on every line.
      2) build a table of frequencies of this frequency (meta-frequency?),
         e.g.  'x occurred 5 times in 10 rows, 6 times in 1000 rows,
         7 times in 2 rows'
      3) use the mode of the meta-frequency to determine the /expected/
         frequency for that character
      4) find out how often the character actually meets that goal
      5) the character that best meets its goal is the delimiter
    For performance reasons, the data is evaluated in chunks, so it can
    try and evaluate the smallest portion of the data possible, evaluating
    additional chunks as necessary.
    """

    data = list(filter(None, data.split('\n')))

    ascii = [chr(c) for c in range(127)] # 7-bit ASCII

    # build frequency tables
    chunkLength = min(10, len(data))
    # minimum consistency threshold
    threshold = 0.8
    # decrease threshold
    if chunkLength < 10:
        threshold = 0.6
    charFrequency = {}
    modes = {}
    delims = {}
    start, end = 0, min(chunkLength, len(data))
    total = 0
    while start < len(data):
        for line in data[start:end]:
            for char in ascii:
                metaFrequency = charFrequency.get(char, {})
                # must count even if frequency is 0
                freq = line.count(char)
                # value is the mode
                metaFrequency[freq] = metaFrequency.get(freq, 0) + 1
                charFrequency[char] = metaFrequency

        for char in list(charFrequency.keys()):
            items = list(charFrequency[char].items())
            if len(items) == 1 and items[0][0] == 0:
                continue
            # get the mode of the frequencies
            if len(items) > 1:
                modes[char] = reduce(lambda a, b: a[1] > b[1] and a or b,
                                     items)
                # adjust the mode - subtract the sum of all
                # other frequencies
                items.remove(modes[char])
                modes[char] = (modes[char][0], modes[char][1]
                               - reduce(lambda a, b: (0, a[1] + b[1]),
                                        items)[1])
            else:
                modes[char] = items[0]

        # build a list of possible delimiters
        modeList = list(modes.items())
        total += chunkLength
        # (rows of consistent data) / (number of rows) = 100%
        consistency = 1.0
        while len(delims) == 0 and consistency >= threshold:
            for k, v in modeList:
                if v[0] > 0 and v[1] > 0:
                    if ((v[1]/float(total)) >= consistency and
                        (delimiters is None or k in delimiters)):
                        delims[k] = v
            consistency -= 0.01

        if len(delims) == 1:
            delim = list(delims.keys())[0]
            skipinitialspace = (data[0].count(delim) ==
                                data[0].count("%c " % delim))
            return (delim, skipinitialspace)

        # analyze another chunkLength lines
        start = end
        chunkLength = min(chunkLength, len(data) - total)
        end += chunkLength

    if not delims:
        return ('', 0)

    # if there's more than one, fall back to a 'preferred' list
    if len(delims) > 1:
        for d in preferred:
            if d in list(delims.keys()):
                skipinitialspace = (data[0].count(d) ==
                                    data[0].count("%c " % d))
                return (d, skipinitialspace)

    # nothing else indicates a preference, pick the character that
    # dominates(?)
    items = [(v,k) for (k,v) in list(delims.items())]
    items.sort()
    delim = items[-1][1]

    skipinitialspace = (data[0].count(delim) ==
                        data[0].count("%c " % delim))
    return (delim, skipinitialspace)