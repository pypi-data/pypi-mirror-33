from anycsv.exceptions import FileSizeException
from anycsv.io_tools import BufferedAutoEncodingStream

from tests.test_encoding_detection import _create_table


def test_read_all(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200)

    ios = BufferedAutoEncodingStream(csv, max_buffer=50)

    for i, line in enumerate(ios):
        pass
    assert i == 200
    assert ios.digest is not None


def test_file(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200)

    ios = BufferedAutoEncodingStream(csv, max_buffer=50)

    first_line = ios.readline()
    ios.reset()
    re_first_line = ios.readline()

    assert first_line == re_first_line


def test_buffer_not_reset(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200)

    ios = BufferedAutoEncodingStream(csv, max_buffer=10)

    [next(ios) for _ in range(12)]

    try:
        ios.reset()
    except Exception as e:
        assert isinstance(e, IOError)


def test_max_file_size(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200)

    ios = BufferedAutoEncodingStream(csv, max_buffer=10, max_file_size=1024)


    try:
        for row in ios:
            pass

    except Exception as e:
        assert isinstance(e, FileSizeException)


def test_file_gzipped(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200, gzipped=True)

    ios = BufferedAutoEncodingStream(csv, max_buffer=50)

    first_line = ios.readline()
    ios.reset()
    re_first_line = ios.readline()

    assert first_line == re_first_line


def test_http(tmpdir):

    csv = "https://datascience.ai.wu.ac.at/ws1718_dataprocessing1_1823/data/allcampusrooms.csv"

    ios = BufferedAutoEncodingStream(csv, max_buffer=50)

    first_line = ios.readline()
    ios.reset()
    re_first_line = ios.readline()

    assert first_line == re_first_line


def test_buffer(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200)

    max_buffer=50
    ios = BufferedAutoEncodingStream(csv, max_buffer=max_buffer)

    c=0
    cnt=b''
    for l in ios:
        c+=1
        cnt+=l
        if c>=max_buffer:
            break

    ios.reset()
    c = 0
    re_cnt = b''
    for l in ios:
        c += 1
        re_cnt += l
        if c >= max_buffer:
            break

    assert len(cnt) == len(re_cnt)
    assert cnt == re_cnt

def test_buffer_gzipped(tmpdir):
    p = tmpdir.mkdir("tmp.csvs").mkdir("data")
    csv = _create_table(p, rows=200, gzipped=True)

    max_buffer=50
    ios = BufferedAutoEncodingStream(csv, max_buffer=max_buffer)

    c=0
    cnt=b''
    for l in ios:
        c+=1
        cnt+=l
        if c>=max_buffer:
            break

    ios.reset()
    c = 0
    re_cnt = b''
    for l in ios:
        c += 1
        re_cnt += l
        if c >= max_buffer:
            break

    assert len(cnt) == len(re_cnt)
    assert cnt == re_cnt


def test_buffer_gzipped(tmpdir):
    csv = "https://datascience.ai.wu.ac.at/ws1718_dataprocessing1_1823/data/allcampusrooms.csv"
    max_buffer=50
    ios = BufferedAutoEncodingStream(csv, max_buffer=max_buffer)

    c=0
    cnt=b''
    for l in ios:
        c+=1
        cnt+=l
        if c>=max_buffer:
            break

    ios.reset()
    c = 0
    re_cnt = b''
    for l in ios:
        c += 1
        re_cnt += l
        if c >= max_buffer:
            break

    assert len(cnt) == len(re_cnt)
    assert cnt == re_cnt


