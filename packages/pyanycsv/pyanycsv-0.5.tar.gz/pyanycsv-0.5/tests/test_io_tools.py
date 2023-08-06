

from anycsv import io_tools
from requests.exceptions import MissingSchema, ConnectTimeout, HTTPError


def test_file_not_available():

    csv="notthere"
    try:
        io_tools.getContentFromDisk(csv)
    except Exception as e:
        assert isinstance(e,FileNotFoundError)


def test_url_missing_schema():

    csv="notthere"
    try:
        io_tools.getContentAndHeaderFromWeb(csv)
    except Exception as e:
        assert isinstance(e,MissingSchema)

def test_url_timeout():
    csv = "http://localhost.com/test.csv"
    try:
        io_tools.getContentAndHeaderFromWeb(csv)
    except Exception as e:
        assert isinstance(e, ConnectTimeout)

def test_url_not_found():
    csv = "http://data.wu.ac.at/test.csv"
    try:
        io_tools.getContentAndHeaderFromWeb(csv)
    except Exception as e:
        assert isinstance(e, HTTPError)