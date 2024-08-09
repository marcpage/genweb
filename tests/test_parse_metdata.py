#!/usr/bin/env python3

""" Test functionality in parsing the metadata """


from os.path import join, dirname
from tempfile import TemporaryDirectory

from genweb.parse_metadata import read_xml, validate_settings, load_metadata
from genweb.parse_metadata import load_inlines

from genweb import parse_metadata


DATA_DIR = join(dirname(__file__), "data")


def test_basic() -> None:
    results = read_xml(join(DATA_DIR, "test.xml"))
    assert results["mod_date"] == "2015-03-21"
    assert results["path"] == "JonesCaleb1765SmithMary1724"
    assert results["type"] == "inline"
    assert results["file"] == "0000000000JonesCaleb1765SmithMary1724.src"
    assert "JonesMargaret1804BrownElisabeth1772" in results["people"]
    assert len(results["people"]) == 11, len(results["people"])
    assert results["title"] == "Caleb Jones (1765-1840) Bio"


class Mock:
    def __init__(self):
        self.out = ""
        self.code = None

    def mock_print(self, message):
        self.out += message + "\n"

    def mock_exit(self, code):
        self.code = code

    def reset(self):
        self.out = ""
        self.code = None


def test_validate_settings() -> None:
    mock = Mock()

    parse_metadata.PRINT = mock.mock_print
    parse_metadata.RETURN_CODE = mock.mock_exit

    settings = {"xmldir": None, "srcdir": None, "finalyaml": None}
    validate_settings(settings)
    assert mock.code is None, mock.code
    assert mock.out == "", mock.out
    mock.reset()

    settings = {}
    validate_settings(settings)
    assert mock.code == 1, mock.code
    assert mock.out != "", mock.out
    mock.reset()


def test_load_metadata() -> None:
    mock = Mock()
    parse_metadata.PRINT = mock.mock_print
    metadata = load_metadata(DATA_DIR)
    assert "test" in metadata
    assert metadata["test"]["type"] == "inline", metadata
    assert metadata["test"]["path"] == "JonesCaleb1765SmithMary1724", metadata


def test_load_inlines() -> None:
    mock = Mock()
    parse_metadata.PRINT = mock.mock_print

    with TemporaryDirectory() as working_dir:
        metadata = {
            "1": {"file": "inline.src", "type": "inline"},
            "2": {"file": "missing.src", "type": "inline"},
        }

        with open(join(working_dir, "inline.src"), "w", encoding="utf-8") as file:
            file.write("the inline contents")

        load_inlines(metadata, working_dir)
        assert metadata["1"]["contents"] == "the inline contents", [
            metadata["1"]["contents"]
        ]
        assert "contents" not in metadata["2"], metadata
        assert "inline src missing" in mock.out, [mock.out]
        assert "missing.src" in mock.out, [mock.out]


if __name__ == "__main__":
    test_basic()
    test_load_metadata()
    test_validate_settings()
    test_load_inlines()
