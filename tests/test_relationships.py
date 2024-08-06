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
    assert any(i.wife for i in gedcom.values()), gedcom
    assert any(i.husband for i in gedcom.values()), gedcom
    assert not all(i.wife for i in gedcom.values()), gedcom
    assert not all(i.husband for i in gedcom.values()), gedcom
    assert sum(len(i.wife) == 1 for i in gedcom.values()) == 1, gedcom
    assert sum(len(i.husband) == 1 for i in gedcom.values()) == 1, gedcom


def test_remarriage() -> None:
    gedcom = load_gedcom(join(DATA_DIR, "REMARR.GED"))
    assert len(gedcom) == 3, gedcom
    assert any(i.wife for i in gedcom.values()), gedcom
    assert any(i.husband for i in gedcom.values()), gedcom
    assert not all(i.wife for i in gedcom.values()), gedcom
    assert not all(i.husband for i in gedcom.values()), gedcom
    assert sum(len(i.wife) == 1 for i in gedcom.values()) == 2, gedcom
    assert sum(len(i.husband) == 2 for i in gedcom.values()) == 1, gedcom


def test_general() -> None:
    gedcom = load_gedcom(join(DATA_DIR, "555SAMPLE.GED"))
    assert len(gedcom) == 3, gedcom
    assert sum(i.father is not None for i in gedcom.values()) == 1, gedcom
    assert sum(i.mother is not None for i in gedcom.values()) == 1, gedcom
    assert sum(len(i.wife) for i in gedcom.values()) == 1, gedcom
    assert sum(len(i.husband) for i in gedcom.values()) == 1, gedcom


if __name__ == "__main__":
    test_empty()
    test_marriage()
    test_remarriage()
    test_general()
