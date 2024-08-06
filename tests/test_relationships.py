#!/usr/bin/env python3

""" Tests the relationships module """

from os.path import join, dirname

from genweb.relationships import load_gedcom


DATA_DIR = join(dirname(__file__), "data")


def test_empty() -> None:
    gedcom = load_gedcom(join(DATA_DIR, "MINIMAL555.GED"))
    assert len(gedcom) == 0, gedcom


def test_marriage() -> None:
    gedcom = load_gedcom(join(DATA_DIR, "SSMARR.GED"))
    assert len(gedcom) == 2, gedcom
    assert all(len(i.spouses) == 1 for i in gedcom.values()), gedcom
    assert all(i.gender == "M" for i in gedcom.values()), gedcom
    assert not all(i.children for i in gedcom.values()), gedcom


def test_remarriage() -> None:
    gedcom = load_gedcom(join(DATA_DIR, "REMARR.GED"))
    assert len(gedcom) == 3, gedcom
    assert any(i.spouses for i in gedcom.values()), gedcom
    assert sum(len(i.spouses) == 1 for i in gedcom.values()) == 2, gedcom
    assert sum(len(i.spouses) == 2 for i in gedcom.values()) == 1, gedcom
    assert sum(i.gender == "M" for i in gedcom.values()) == 2, gedcom
    assert sum(i.gender == "F" for i in gedcom.values()) == 1, gedcom
    assert not all(i.children for i in gedcom.values()), gedcom


def test_general() -> None:
    gedcom = load_gedcom(join(DATA_DIR, "555SAMPLE.GED"))
    assert len(gedcom) == 3, gedcom
    assert sum(len(i.parents) == 2 for i in gedcom.values()) == 1, gedcom
    assert sum(len(i.spouses) for i in gedcom.values()) == 2, gedcom
    assert sum(i.gender == "M" for i in gedcom.values()) == 2, gedcom
    assert sum(i.gender == "F" for i in gedcom.values()) == 1, gedcom
    assert sum(len(i.children) for i in gedcom.values()) == 2, gedcom
    assert all(len(i.children) in {0, 1} for i in gedcom.values()), gedcom


if __name__ == "__main__":
    test_empty()
    test_marriage()
    test_remarriage()
    test_general()
