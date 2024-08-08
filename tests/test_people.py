#!/usr/bin/env python3


""" Test the People object """


from types import SimpleNamespace
from datetime import date

from genweb.people import People
import genweb.people


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
    assert list(people.values())[0].given == "John Smith", people.values()
    assert list(people.items())[0][0] == list(people.items())[0][1].id, people.items()
    # people2 = People(gedcom)
    # assert people == people2, [people, people2]
    assert [i for i in people][0] == "DoeJohnS1973-"
    assert people.get("false", None) is None
    assert people.get("DoeJohnS1973-", None).id == "DoeJohnS1973-"


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


def test_find_mother() -> None:
    genweb.people.PRINT = lambda _: None
    people = {
        "1": SimpleNamespace(parents=["2", "3", "4", "5"], gender="F", surname="Smith"),
        "2": SimpleNamespace(parents=[], gender="M", surname="Smith"),
        "3": SimpleNamespace(parents=[], gender="F", surname="Smith"),
        "4": SimpleNamespace(parents=[], gender="F", surname="Jones"),
        "5": SimpleNamespace(parents=[], gender="F", surname="Brown"),
    }
    result = People._find_mother(  # pylint: disable=protected-access
        people["1"], people
    )
    assert result.surname in {"Jones", "Brown"}, result


def test_match_score() -> None:
    identifiers = [
        ("hello", "hello", 1.0),
        ("hello", "hello world", 0.25),
        ("abc", "xyz", 0.0),
        ("SmithZoeR2022AdamsenAndreaM0000", "SmithZoeR2022AdamsenAndreaM1987", 0.58),
        (
            "SmithAddison1819BarrPatty1786",
            "SmithAddiSmithAddison1819BarrPatty1786son1820",
            0.48,
        ),
    ]
    for first, second, expected in identifiers:
        score = People._match_score(first, second)
        assert abs(score - expected) < 0.01, [first, second, score, expected]

    with open("people ids.txt", "r", encoding="utf-8") as file:
        ids = [l.strip() for l in file.readlines()]

    scores = []
    ids.sort()

    for first_index, first in enumerate(ids):
        print(f"{first_index} / {len(ids)}")
        for second in ids[first_index + 1 : first_index + 20]:
            scores.append((People._match_score(first, second), first, second))

    scores.sort(reverse=False)
    scores = scores[-500:]
    scores.sort(reverse=True)
    with open("all scores.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(f"{s:0.2f}\t{o}\t{t}" for s, o, t in scores))


if __name__ == "__main__":
    test_dict_operators()
    test_basic()
    test_middle_initial()
    test_no_birthdate()
    test_find_mother()
    test_match_score()
