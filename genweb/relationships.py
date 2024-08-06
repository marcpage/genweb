#!/usr/bin/env python3


""" Load relationship data from GEDCOM file """


from types import SimpleNamespace

from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement


def parse_individual(individual: IndividualElement) -> SimpleNamespace:
    """Parses out a GEDCOM individual

    Args:
        individual (IndividualElement): individual information

    Returns:
        SimpleNamespace: Objects that has given, surname, birthdate, id, father, mother, and
                            husband and wife sets
    """
    return SimpleNamespace(
        given=individual.get_name()[0],
        surname=individual.get_name()[1],
        birthdate=individual.get_birth_data()[0],
        deathdate=individual.get_death_data()[0],
        gender=individual.get_gender(),
        id=individual.get_pointer(),
        spouses=set(),
        parents=set(),
        children=set(),
    )


def get_field(family: FamilyElement, field: str) -> [str]:
    """Given a GEDCOM family, extract the fields of the given type

    Args:
        family (FamilyElement): The family record to evaluate
        field (str): The type of the field

    Returns:
        [str]: A list of the fields of the given type
    """
    return [e.get_value() for e in family.get_child_elements() if e.get_tag() == field]


def get_spouses(family: FamilyElement) -> [str]:
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


def load_gedcom(path: str) -> dict[str, dict]:
    """Returns a mapping of individual id to a dscription of that individual

    Args:
        path (str): The path to the GEDCOM file to parse

    Returns:
        dict[str, dict]: Map of GEDCOM id for the indidivual to an object that has
                            given, surname, birthdate, id, father, mother, and
                            husband and wife sets
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
