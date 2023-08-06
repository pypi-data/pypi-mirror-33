import pytest
from anycsv.encoding import detect_encoding
from anycsv.io_tools import BufferedAutoEncodingStream
from anycsv import dialect as D
from tests import create_random_dummy_table, _create_table


def test_file_gzipped(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200, gzipped=True)

    ios = BufferedAutoEncodingStream(csv, max_buffer=50)

    dialect = D.guessDialect(ios, 'utf-8')

    import csv
    assert dialect.delimiter == csv.unix_dialect.delimiter


def test_single_file():
    csv = "/Users/jumbrich/data/mimesis_csvs/encoding/latin.csv"
    ios = BufferedAutoEncodingStream(csv, max_buffer=50)

    dialect = D.guessDialect(ios, 'cp737')

    import csv
    assert dialect.delimiter == csv.unix_dialect.delimiter