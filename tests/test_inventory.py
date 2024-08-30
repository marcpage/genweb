#!/usr/bin/env python3


""" Test Artifacts """


from os import makedirs, utime
from os.path import dirname, relpath, basename, join
from tempfile import TemporaryDirectory
from time import time

from genweb.inventory import Artifacts


def test_suffixed() -> None:
    artifacts = Artifacts(dirname(__file__))
    assert "data/fake.jpg" in artifacts.suffixed("ta/fake.jpg")


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


def create_file(path: str, contents: str):
    makedirs(dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)


def test_add() -> None:
    with TemporaryDirectory() as working_dir:
        create_file(join(working_dir, "file1.txt"), "file1")
        create_file(join(working_dir, "file2.txt"), "file2")
        create_file(join(working_dir, "dir/file3.txt"), "file3")
        artifacts = Artifacts(working_dir)
        create_file(join(working_dir, "dir/file4.txt"), "file4")
        artifacts.add("dir/file4.txt")
        artifacts.add("file1.txt")

        try:
            artifacts.add("dir/file5.txt")
            raise AssertionError("dir/file5.txt should have failed")

        except AssertionError:
            pass

        lost = {"file2.txt", "dir/file3.txt"}
        assert set(artifacts.lost()) == lost, artifacts.lost()


def test_hash() -> None:
    with TemporaryDirectory() as working_dir:
        create_file(join(working_dir, "file1.txt"), "")
        create_file(join(working_dir, "dir/file2.txt"), "2")
        artifacts = Artifacts(working_dir)
        hash_empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        hash_2 = "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35"
        assert artifacts.hash("file1.txt") == hash_empty, artifacts.hash("file1.txt")
        assert artifacts.hash("dir/file2.txt") == hash_2, artifacts.hash(
            "dir/file2.txt"
        )
        create_file(join(working_dir, "dir/file2.txt"), "2 ")
        hash_2_space = (
            "5749fdd6b67e4204b3047ba33540bc87f60c84d784a46c6307c78299f8fa67e9"
        )
        artifacts = Artifacts(working_dir)
        assert artifacts.hash("file1.txt") == hash_empty, artifacts.hash("file1.txt")
        assert artifacts.hash("dir/file2.txt") == hash_2_space, artifacts.hash(
            "dir/file2.txt"
        )
        minute_ago = time() - 60
        utime(join(working_dir, "file1.txt"), (minute_ago, minute_ago))
        assert artifacts.hash("file1.txt") == hash_empty, artifacts.hash("file1.txt")


if __name__ == "__main__":
    test_basic()
    test_suffixed()
    test_add()
    test_hash()
