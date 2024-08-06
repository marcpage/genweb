#!/usr/bin/env python3

""" Test parsing the yaml """


from os.path import dirname, join


from genweb.metadata import load


DATA_DIR = join(dirname(__file__), "data")


def test_load() -> None:
    metadata = load(join(DATA_DIR, "example.yml"))
    assert len(metadata) == 3, ",".join(metadata.keys())
    assert "0000000000SmithCaleb1765JonesMary1724" in metadata
    assert len(metadata["0000000000SmithCaleb1765JonesMary1724"]["people"]) == 11
    assert (
        "BrownElisabeth1772-"
        in metadata["0000000000SmithCaleb1765JonesMary1724"]["people"]
    )
    assert "1700000000WilliamsJohn1665DavisRebecca1639" in metadata
    assert metadata["1700000000WilliamsJohn1665DavisRebecca1639"]["width"] == 600


if __name__ == "__main__":
    test_load()
