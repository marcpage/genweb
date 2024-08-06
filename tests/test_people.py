#!/usr/bin/env python3


""" Test the People object """


from types import SimpleNamespace
from datetime import date

from genweb.people import People


def test_basic() -> None:
    gedcom_list = [
        SimpleNamespace(
            id="1",
            given="John",
            surname="Doe",
            gender="M",
            birthdate=date(1973, 6, 30),
            parents=set(),
            spouses={"2"},
            children={"3", "4"},
        ),
        SimpleNamespace(
            id="2",
            given="Sally",
            surname="Smith",
            gender="F",
            birthdate=date(1971, 12, 14),
            parents=set(),
            spouses={"1"},
            children={"3", "4"},
        ),
        SimpleNamespace(
            id="3",
            given="James",
            surname="Doe",
            gender="M",
            birthdate=date(2004, 7, 31),
            parents={"2", "1"},
            spouses=set(),
            children=set(),
        ),
        SimpleNamespace(
            id="4",
            given="Jane",
            surname="Doe",
            gender="F",
            birthdate=date(2007, 3, 7),
            parents={"2", "1"},
            spouses=set(),
            children=set(),
        ),
    ]
    gedcom = {p.id: p for p in gedcom_list}
    assert len(gedcom) == len(gedcom_list)
    people = People(gedcom)
    assert len(people) == 4, people
    assert "1-" in people, people
    assert "2-" in people, people
    assert "3-2" in people, people
    assert "4-2" in people, people
    assert people["1-"].given == "John", people["1-"]
    assert people["2-"].given == "Sally", people["2-"]
    assert people["3-2"].given == "James", people["3-2"]
    assert people["4-2"].given == "Jane", people["4-2"]


if __name__ == "__main__":
    test_basic()
