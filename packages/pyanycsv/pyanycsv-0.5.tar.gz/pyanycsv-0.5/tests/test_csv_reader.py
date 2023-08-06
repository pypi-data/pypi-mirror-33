import anycsv

from tests import _create_table


def test_file(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200, columns=4, gzipped=True)

    reader = anycsv.reader(csv)

    for row in reader:
        assert len(row) == 4

    assert reader.digest is not None


def test_single_file():
    csv = "/Users/jumbrich/data/mimesis_csvs/encoding/latin.csv"
    reader = anycsv.reader(csv)

    for row in reader:
        assert len(row) == 9

    assert reader.digest is not None
