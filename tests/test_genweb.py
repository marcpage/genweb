#!/usr/bin/env python3

""" Test genweb function """


from types import SimpleNamespace
from tempfile import TemporaryDirectory
from datetime import date

from genweb.genweb import link_people_to_metadata, generate_people_pages
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


if __name__ == "__main__":
    test_link_people_to_metadata()
    test_generate_people_pages()
