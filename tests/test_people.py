#!/usr/bin/env python3


""" Test the People object """


from types import SimpleNamespace
from datetime import date

from genweb.people import People


def test_dict_operators() -> None:
    gedcom_list = [
        SimpleNamespace(
            id="1",
            given="John Smith",
            surname="Doe",
            gender="M",
            birthdate=date(1973, 6, 30),
            parents=set(),
            spouses=set(),
            children=set(),
        ),
    ]

    gedcom = {p.id: p for p in gedcom_list}
    assert len(gedcom) == len(gedcom_list)
    people = People(gedcom)
    assert "DoeJohnS1973-" in repr(people), repr(people)
    assert people.has_key("DoeJohnS1973-"), people
    assert "DoeJohnS1973-" in people.keys(), people


def test_middle_initial() -> None:
    gedcom_list = [
        SimpleNamespace(
            id="1",
            given="John Smith",
            surname="Doe",
            gender="M",
            birthdate=date(1973, 6, 30),
            parents=set(),
            spouses=set(),
            children=set(),
        ),
    ]

    gedcom = {p.id: p for p in gedcom_list}
    assert len(gedcom) == len(gedcom_list)
    people = People(gedcom)
    assert len(people) == 1, people
    assert "DoeJohnS1973-" in people, people
    assert people["DoeJohnS1973-"].given == "John Smith", people["DoeJohnS1973-"].given


def test_no_birthdate() -> None:
    gedcom_list = [
        SimpleNamespace(
            id="1",
            given="John Smith",
            surname="Doe",
            gender="M",
            birthdate=None,
            parents=set(),
            spouses=set(),
            children=set(),
        ),
    ]

    gedcom = {p.id: p for p in gedcom_list}
    assert len(gedcom) == len(gedcom_list)
    people = People(gedcom)
    assert len(people) == 1, people
    assert "DoeJohnS0000-" in people, people
    assert people["DoeJohnS0000-"].given == "John Smith", people["DoeJohnS0000-"].given

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
    assert "DoeJohn1973-" in people, people
    assert "SmithSally1971-" in people, people
    assert "DoeJane2007SmithSally1971" in people, people
    assert "DoeJames2004SmithSally1971" in people, people
    assert people["DoeJohn1973-"].given == "John", people["DoeJohn1973-"]
    assert people["SmithSally1971-"].given == "Sally", people["SmithSally1971-"]
    assert people["DoeJames2004SmithSally1971"].given == "James", people[
        "DoeJames2004SmithSally1971"
    ]
    assert people["DoeJane2007SmithSally1971"].given == "Jane", people[
        "DoeJane2007SmithSally1971"
    ]


if __name__ == "__main__":
    test_dict_operators()
    test_basic()
    test_middle_initial()
    test_no_birthdate()
