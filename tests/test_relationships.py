#!/usr/bin/env python3

""" Tests the relationships module """

from os.path import join, dirname
from datetime import date

from genweb.relationships import load_gedcom, parse_date


DATA_DIR = join(dirname(__file__), "data")


def test_bad_date_parse() -> None:
    try:
        _ = parse_date("garbage date")
        raise AssertionError("We should have failed")
    except ValueError:
        pass


def test_date_parse() -> None:
    dates = {
        "CHILD": date(1, 1, 1),
        "23 JULI 1875": date(1875, 7, 23),
        "AFTER 1880 CENSU": date(1880, 1, 1),
        "D 2 SEP 1854": date(1854, 9, 2),
        "4 FEB 1784 (AE 49)": date(1784, 2, 4),
        "29 FEB 1897": date(1897, 2, 28),
        "NOT SPECIFIED": date(1, 1, 1),
        "SINCE 1733": date(1733, 1, 1),
        "WFT EST. 1695": date(1695, 1, 1),
        "(OVER 70) 10 MAY 1807": date(1807, 5, 10),
        "INFANT": date(1, 1, 1),
        "@ 1740S ?": date(1740, 1, 1),
        "25 FEB 1747–8": date(1747, 2, 25),
        "12 FEB": date(1, 2, 12),
        "1824–1825": date(1824, 1, 1),
        "1626 OR 1627": date(1626, 1, 1),
        "5 JANUARY 1297": date(1297, 1, 5),
        "844": date(844, 1, 1),
        "BET 11 DEC 1669 AND 1672": date(1669, 12, 11),
        "DEAD": date(1, 1, 1),
        "EST 1843": date(1843, 1, 1),
        "AFT 1769": date(1769, 1, 1),
        "CA 1837": date(1837, 1, 1),
        "ABT 1787": date(1787, 1, 1),
        "3 NOV 1726 OR 3 NOV 1727": date(1726, 11, 3),
        "12 JAN 1727/8": date(1727, 1, 12),
        "FROM 5 OCT 1831 TO 8 MAY 1832": date(1831, 10, 5),
        "CALC 1931": date(1931, 1, 1),
        "1900": date(1900, 1, 1),
        "NOV 1266": date(1266, 11, 1),
        "BEF 1828": date(1828, 1, 1),
        "16 Mar 1864": date(1864, 3, 16),
        None: None,
    }

    for description, value in dates.items():
        assert parse_date(description) == value, [
            description,
            value,
            parse_date(description),
        ]


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
    test_bad_date_parse()
    test_date_parse()
    test_empty()
    test_marriage()
    test_remarriage()
    test_general()
