#!/usr/bin/env python3


""" Load relationship data from GEDCOM file """


from types import SimpleNamespace
from datetime import date, datetime
from re import compile as regex, IGNORECASE

from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement


BEF_PATTERN = regex(
    r"^(BEF|CALC|ABT|CA|AFT|EST|WFT EST.|SINCE|D|AFTER)\s+(.+?)\s*(CENSU)?$", IGNORECASE
)
RANGE_PATTERN = regex(r"^(FROM|BET) (.+) (TO|AND) (.+)$", IGNORECASE)
CHOICE_PATTERN = regex(r"^(.+) OR (.+)$", IGNORECASE)
SMALL_YEAR = regex(r"^\d{3}$")
PARENTHESIS_PREFIX_PATTERN = regex(r"^\(.+\)\s*(.+)$")
PARENTHESIS_SUFFIX_PATTERN = regex(r"^(.+)\s*\(.+\)$")
DATE_PARSING_FORMATS = [
    "%d %b %Y",  # 16 Mar 1864
    "%b %Y",  # NOV 1266
    "%d %B %Y",  # 16 Mar 1864
    "%Y",  # 1900
]


def parse_date_regex(given_date: str) -> date | None:
    """Checks regular expressions to extract date to parse

    Args:
        given_date (str): The date to parse

    Returns:
        date | None: The parsed date or None if no regex matched
    """
    is_range = RANGE_PATTERN.match(given_date)
    is_choice = CHOICE_PATTERN.match(given_date)
    is_bef = BEF_PATTERN.match(given_date)
    is_small = SMALL_YEAR.match(given_date)
    is_parenthesis_prefix = PARENTHESIS_PREFIX_PATTERN.match(given_date)
    is_parenthesis_suffix = PARENTHESIS_SUFFIX_PATTERN.match(given_date)
    result = None

    if is_small:  # 844
        result = date(int(given_date), 1, 1)

    elif is_range:  # FROM 5 OCT 1831 TO 8 MAY 1832
        result = parse_date(is_range.group(2))

    elif is_choice:  # 3 NOV 1726 OR 3 NOV 1727
        result = parse_date(is_choice.group(1))

    elif is_bef:  # BEF 1863, CALC 1931
        result = parse_date(is_bef.group(2))

    elif is_parenthesis_prefix:  # (OVER 70) 10 MAY 1807
        result = parse_date(is_parenthesis_prefix.group(1))

    elif is_parenthesis_suffix:  # 4 FEB 1784 (AE 49)
        result = parse_date(is_parenthesis_suffix.group(1))

    return result


def parse_date(given_date: str | None) -> date:
    """Given a date string, parse it into a date object

    Args:
        given_date (str): The date string

    Returns:
        date: The date object that represents the `given_date`
    """
    if given_date is None or given_date == "":
        return None

    # @ 1740S ?
    given_date = (
        given_date.strip("@")
        .strip("?")
        .strip()
        .rstrip("S")
        .rstrip("s")
        .replace("JULI", "JUL")
    )

    if given_date in {"DEAD", "INFANT", "UNKNOWN", "NOT SPECIFIED", "CHILD"}:
        return date(1, 1, 1)

    for character in ["/", "-", "–"]:
        if character in given_date:  # 12 JAN 1727/8
            given_date = given_date.split(character)[0]

    parsed = parse_date_regex(given_date)

    if parsed:
        return parsed

    for date_format in DATE_PARSING_FORMATS:
        try:
            return datetime.strptime(given_date, date_format).date()
        except ValueError:
            pass

    try:  # 29 FEB 1897 - no leap years between 1896 and 1904
        if given_date.lower().startswith("29 feb"):
            return parse_date("28" + given_date[2:])
    except ValueError:
        pass

    try:
        mon_day = datetime.strptime(given_date, "%d %b").date()  # 12 FEB
        return date(1, mon_day.month, mon_day.day)
    except ValueError as error:
        raise ValueError(f"Unable to parse date: '{given_date}': {error}") from error


def parse_individual(individual: IndividualElement) -> SimpleNamespace:
    """Parses out a GEDCOM individual

    Args:
        individual (IndividualElement): individual information

    Returns:
        SimpleNamespace: Objects that has given, surname, birthdate, id, and
                            spouses, children and parents sets
    """
    return SimpleNamespace(
        given=individual.get_name()[0],
        surname=individual.get_name()[1],
        birthdate=parse_date(individual.get_birth_data()[0]),
        deathdate=parse_date(individual.get_death_data()[0]),
        gender=individual.get_gender(),
        id=individual.get_pointer(),
        spouses=set(),
        parents=set(),
        children=set(),
        metadata=[],
    )


def person_json(person: SimpleNamespace) -> dict[str, any]:
    """Gets a JSON representation of a person

    Args:
        person (SimpleNamespace): The person to describe

    Returns:
        dict[str, any]: The dictionary that is suitable to convert to JSON
    """
    return {
        "given": person.given,
        "surname": person.surname,
        "birthdate": person.birthdate.strftime("%Y-%m-%d") if person.birthdate else "?",
        "deathdate": person.deathdate.strftime("%Y-%m-%d") if person.deathdate else "?",
        "gender": person.gender,
        "id": person.id,
        "spouses": list(person.spouses),
        "parents": list(person.parents),
        "children": list(person.children),
        "metadata": list(person.metadata),
    }


def get_field(family: FamilyElement, field: str) -> list[str]:
    """Given a GEDCOM family, extract the fields of the given type

    Args:
        family (FamilyElement): The family record to evaluate
        field (str): The type of the field

    Returns:
        [str]: A list of the fields of the given type
    """
    return [e.get_value() for e in family.get_child_elements() if e.get_tag() == field]


def get_spouses(family: FamilyElement) -> list[str]:
    """Get the husband or wife of the family

    Args:
        family (FamilyElement): The family to evaluate

    Returns:
        str: The identifier for the requested spouse, or None if not found
    """
    spouses = set(get_field(family, "HUSB"))
    spouses.update(set(get_field(family, "WIFE")))
    assert len(spouses) in {0, 1, 2}, family
    return spouses


def parse_family(family: FamilyElement) -> dict:
    """Parses a GEDCOM family record

    Args:
        family (FamilyElement): The family record to parse

    Returns:
        dict: An object with wife, husband, and a list of children ids
    """
    return SimpleNamespace(
        spouses=get_spouses(family),
        children=set(get_field(family, "CHIL")),
    )


def load_gedcom(path: str) -> dict[str, SimpleNamespace]:
    """Returns a mapping of individual id to a dscription of that individual

    Args:
        path (str): The path to the GEDCOM file to parse

    Returns:
        dict[str, SimpleNamespace]: Objects that has given, surname, birthdate, id, and
                            spouses, children and parents sets
    """
    gedcom = Parser()
    gedcom.parse_file(path, strict=True)

    individuals = {
        e.get_pointer(): parse_individual(e)
        for e in gedcom.get_root_child_elements()
        if isinstance(e, IndividualElement)
    }
    families = [
        parse_family(e)
        for e in gedcom.get_root_child_elements()
        if isinstance(e, FamilyElement)
    ]

    for family in families:
        for spouse in family.spouses:
            individuals[spouse].spouses |= family.spouses - {spouse}
            individuals[spouse].children |= family.children

        for child in family.children:
            individuals[child].parents |= family.spouses

    return individuals
