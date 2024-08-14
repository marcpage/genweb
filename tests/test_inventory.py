#!/usr/bin/env python3


""" Test Artifacts """


from os.path import dirname, relpath, basename

from genweb.inventory import Artifacts


def test_basic() -> None:
    artifacts = Artifacts(dirname(__file__))
    assert relpath(__file__, artifacts.directory) in artifacts.lost(), [
        relpath(__file__, artifacts.directory),
        artifacts.lost(),
    ]
    assert "data/bad.xml" in artifacts.lost()
    assert "test_people.py" in artifacts.lost()
    assert "data/test.xml" in artifacts.lost()
    assert artifacts.has_file(relpath(__file__, artifacts.directory))
    assert artifacts.has_file("data/bad.xml")
    assert artifacts.has_file("data/test.xml")
    assert artifacts.has_file("test_people.py")
    assert len(artifacts.paths(basename(__file__))) == 1
    assert len(artifacts.paths("bad.xml")) == 1
    assert len(artifacts.paths("test.xml")) == 1
    assert len(artifacts.paths("test_people.py")) == 1
    assert len(artifacts.paths("bogus")) == 0
    assert artifacts.has_dir("data")
    assert not artifacts.has_dir("bogus")
    assert "data/bad.xml" in artifacts.files_under("data")
    assert "data/test.xml" in artifacts.files_under("data")
    artifacts.add(relpath(__file__, artifacts.directory))
    artifacts.add("data/bad.xml")
    artifacts.add("data/bad.xml")
    assert relpath(__file__, artifacts.directory) not in artifacts.lost(), [
        relpath(__file__, artifacts.directory),
        artifacts.lost(),
    ]
    assert "data/bad.xml" not in artifacts.lost()
    assert "test_people.py" in artifacts.lost()
    assert "data/test.xml" in artifacts.lost()
    assert len(artifacts.paths(basename(__file__))) == 1
    assert len(artifacts.paths("bad.xml")) == 1
    assert len(artifacts.paths("test.xml")) == 1
    assert len(artifacts.paths("test_people.py")) == 1
    assert len(artifacts.paths("bogus")) == 0
    assert artifacts.has_dir("data")
    assert not artifacts.has_dir("bogus")
    assert artifacts.has_file(relpath(__file__, artifacts.directory))
    assert artifacts.has_file("data/bad.xml")
    assert artifacts.has_file("data/test.xml")
    assert artifacts.has_file("test_people.py")
    assert "data/bad.xml" in artifacts.files_under("data")
    assert "data/test.xml" in artifacts.files_under("data")


if __name__ == "__main__":
    test_basic()
