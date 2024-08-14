#!/usr/bin/env python3

""" Test genweb function """

from os import makedirs
from os.path import join, isfile, dirname
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from datetime import date
from shutil import copytree, copy

from genweb.genweb import link_people_to_metadata, generate_people_pages
from genweb.genweb import copy_static_files, copy_metadata_files
from genweb.inventory import Artifacts
import genweb.genweb


def test_generate_people_pages() -> None:
    people = {
        "1": SimpleNamespace(
            id="1",
            parents=["2", "3", "4", "5"],
            gender="F",
            surname="Smith",
            metadata=["1"],
            given="Sally",
            birthdate=date.today(),
            deathdate=date.today(),
            spouses=set(),
            children=set(),
        ),
        "2": SimpleNamespace(
            id="2",
            parents=[],
            gender="M",
            surname="Smith",
            metadata=["2"],
            given="John",
            birthdate=date.today(),
            deathdate=date.today(),
            spouses=set(),
            children=set(),
        ),
        "3": SimpleNamespace(parents=[], gender="F", surname="Smith", metadata=[]),
        "4": SimpleNamespace(parents=[], gender="F", surname="Jones", metadata=[]),
        "5": SimpleNamespace(parents=[], gender="F", surname="Brown", metadata=[]),
    }
    metadata = {"1": {"type": "dummy"}, "2": {"type": "dummy"}}
    with TemporaryDirectory() as working_dir:
        generate_people_pages(working_dir, people, metadata)


def test_link_people_to_metadata() -> None:
    genweb.genweb.PRINT = lambda _: None
    people = {"p1": SimpleNamespace(metadata=[])}
    metadata = {"m1": {"people": ["p1", "p2"]}, "m2": {}}
    link_people_to_metadata(people, metadata)
    assert "m1" in people["p1"].metadata, people
    assert len(people["p1"].metadata) == 1, people


def test_copy_static_files() -> None:
    with TemporaryDirectory() as working_dir:
        files = {
            "dir/styles.css": "data/styles.css",
            "images/unknown.jpg": "data/silhouette.jpg",
        }
        copy_static_files(files, working_dir)
        assert isfile(join(working_dir, "dir", "styles.css"))
        assert isfile(join(working_dir, "images", "unknown.jpg"))


def test_copy_metadata_files() -> None:
    genweb.genweb.PRINT = lambda _: None

    with TemporaryDirectory() as src_dir, TemporaryDirectory() as dst_dir:
        copytree(join(dirname(__file__), "data"), join(src_dir, "data"))
        makedirs(join(dst_dir, "foo"))
        copy(
            join(dirname(__file__), "data", "test.xml"),
            join(dst_dir, "foo", "test.xml"),
        )
        artifacts = Artifacts(src_dir)
        metadata = {
            "1": {"type": "picture", "file": "test.xml", "path": "foo"},
            "2": {"type": "unknown"},
            "3": {"type": "picture", "file": "missing.xml", "path": "bar"},
        }
        people = {
            "1": SimpleNamespace(id="1", metadata=["1"]),
            "fake": SimpleNamespace(id="fake", metadata=["1"]),
            "nosho": SimpleNamespace(id="nosho", metadata=[]),
        }
        default_thumbnail = join(src_dir, "data", "fake2.jpg")
        copy_metadata_files(artifacts, dst_dir, metadata, people, default_thumbnail)
        assert isfile(join(dst_dir, "foo", "test.xml"))

        with open(join(dst_dir, "1", "1.jpg"), "r", encoding="utf-8") as file_1:
            fake2_contents = file_1.read()

        assert fake2_contents.startswith("default")

        with open(
            join(dst_dir, "fake", "fake.jpg"), "r", encoding="utf-8"
        ) as file_fake:
            fake_contents = file_fake.read()

        assert fake_contents.startswith("not really an image")


if __name__ == "__main__":
    test_link_people_to_metadata()
    test_generate_people_pages()
    test_copy_static_files()
    test_copy_metadata_files()
