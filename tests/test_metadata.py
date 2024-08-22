#!/usr/bin/env python3

""" Test parsing the yaml """


from os.path import dirname, join
from shutil import copy
from tempfile import TemporaryDirectory


from genweb.metadata import load_yaml, Metadata


DATA_DIR = join(dirname(__file__), "data")


def test_metadata_save() -> None:
    with TemporaryDirectory() as working_dir:
        src_file = join(DATA_DIR, "example.yml")
        metadata_file = join(working_dir, "example.yml")
        copy(src_file, metadata_file)
        metadata = Metadata(metadata_file)
        johns_picture = metadata["1700000000WilliamsJohn1665DavisRebecca1639"]
        johns_picture["width"] = 500
        metadata["1700000000WilliamsJohn1665DavisRebecca1639"] = johns_picture
        assert metadata["1700000000WilliamsJohn1665DavisRebecca1639"]["width"] == 500
        metadata.save()

        metadata = Metadata(metadata_file)
        assert metadata["1700000000WilliamsJohn1665DavisRebecca1639"]["width"] == 500
        metadata.save()

        with open(src_file, "r", encoding="utf-8") as file:
            original = file.read()

        with open(metadata_file, "r", encoding="utf-8") as file:
            copied = file.read()

        assert original == copied, "base metadata file was modified"


def test_metadata_update() -> None:
    metadata = Metadata(join(DATA_DIR, "layered.yml"))
    metadata["0000000000PageMarcA1973HislopMickieL1949"] = {
        "type": "inline",
        "content": "hello",
    }
    original = metadata["0000000000JohnsonSamI1892MillerJane1860"]
    assert "StoriesPersonal0000-" not in original["people"]
    original["people"].append("StoriesPersonal0000-")
    assert (
        "StoriesPersonal0000-"
        not in metadata["0000000000JohnsonSamI1892MillerJane1860"]["people"]
    )
    metadata["0000000000JohnsonSamI1892MillerJane1860"] = original
    assert (
        "StoriesPersonal0000-"
        in metadata["0000000000JohnsonSamI1892MillerJane1860"]["people"]
    )
    assert "0000000000PageMarcA1973HislopMickieL1949" in metadata
    assert metadata["0000000000PageMarcA1973HislopMickieL1949"]["content"] == "hello"
    assert (
        metadata.get("0000000000PageMarcA1973HislopMickieL1949")["content"] == "hello"
    )


def test_metadata() -> None:
    metadata = Metadata(join(DATA_DIR, "layered.yml"))
    assert "0000000000SmithCaleb1765JonesMary1724" in metadata
    assert "0000000000JohnsonSamI1892MillerJane1860" in metadata
    assert "1700000000WilliamsJohn1665DavisRebecca1639" in metadata
    assert (
        "StoriesPersonal0000-"
        not in metadata["0000000000JohnsonSamI1892MillerJane1860"]["people"]
    )
    assert (
        "JohnsonSamI1892MillerJane1860"
        in metadata["0000000000JohnsonSamI1892MillerJane1860"]["people"]
    )
    assert len(metadata) == 3
    assert "600" in repr(metadata), repr(metadata)
    assert metadata.has_key("1700000000WilliamsJohn1665DavisRebecca1639")
    assert "1700000000WilliamsJohn1665DavisRebecca1639" in metadata.keys()
    assert (
        metadata.get("0000000000SmithCaleb1765JonesMary1724", None)["mod_date"]
        == "2015-03-21"
    )
    assert (
        metadata.get("1700000000WilliamsJohn1665DavisRebecca1639", None)["width"] == 600
    )
    assert "1700000000WilliamsJohn1665DavisRebecca1639" in metadata.keys()
    assert [v for v in metadata.values() if v["type"] == "picture"][0]["width"] == 600
    assert [k for k, v in metadata.items() if v["type"] == "inline"][
        0
    ] == "0000000000SmithCaleb1765JonesMary1724"
    assert "0000000000SmithCaleb1765JonesMary1724" in set(metadata)
    assert (
        metadata.get("0000000000SmithCaleb1765JonesMary1724", None)["path"]
        == "SmithCaleb1765JonesMary1724"
    )
    assert metadata.get("false", None) is None
    assert (
        "StoriesPersonal0000-"
        not in metadata.get("0000000000JohnsonSamI1892MillerJane1860", None)["people"]
    )
    assert (
        "StoriesPersonal0000-"
        not in metadata["0000000000JohnsonSamI1892MillerJane1860"]["people"]
    )


def test_load_yaml() -> None:
    metadata = load_yaml(join(DATA_DIR, "example.yml"))
    assert len(metadata) == 6, ",".join(metadata.keys())
    assert "0000000000SmithCaleb1765JonesMary1724" in metadata
    assert len(metadata["0000000000SmithCaleb1765JonesMary1724"]["people"]) == 11
    assert (
        "BrownElisabeth1772-"
        in metadata["0000000000SmithCaleb1765JonesMary1724"]["people"]
    )
    assert "1700000000WilliamsJohn1665DavisRebecca1639" in metadata
    assert metadata["1700000000WilliamsJohn1665DavisRebecca1639"]["width"] == 600


class MockArtifacts:
    def __init__(self):
        self.has_dir_result = True
        self.has_file_result = True
        self.has_file_plus_result = True

    def has_dir(self, path: str) -> bool:
        return self.has_dir_result

    def has_file(self, path: str) -> bool:
        if "/+" in path:
            return self.has_file_plus_result

        return self.has_file_result

    def files_under(self, path: str) -> list:
        return []


def test_get_copy_list() -> None:
    metadata = Metadata(join(DATA_DIR, "example.yml"))
    artifacts = MockArtifacts()
    _ = metadata.get_copy_list(artifacts)
    artifacts.has_file_plus_result = False
    _ = metadata.get_copy_list(artifacts)
    artifacts.has_file_result = False
    _ = metadata.get_copy_list(artifacts)
    artifacts.has_dir_result = False
    _ = metadata.get_copy_list(artifacts)


if __name__ == "__main__":
    test_load_yaml()
    test_metadata()
    test_metadata_update()
    test_metadata_save()
    test_get_copy_list()
