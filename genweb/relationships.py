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
        id=individual.get_pointer(),
        husband=set(),
        wife=set(),
        father=None,
        mother=None,
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


def get_spouse(family: FamilyElement, wife: bool) -> str:
    """Get the husband or wife of the family

    Args:
        family (FamilyElement): The family to evaluate
        wife (bool): Get the wife or the husband

    Returns:
        str: The identifier for the requested spouse, or None if not found
    """
    spouse = get_field(family, "WIFE" if wife else "HUSB")
    assert not spouse or len(spouse) == 1, family
    return spouse[0] if spouse else None


def parse_family(family: FamilyElement) -> dict:
    """Parses a GEDCOM family record

    Args:
        family (FamilyElement): The family record to parse

    Returns:
        dict: An object with wife, husband, and a list of children ids
    """
    return SimpleNamespace(
        husband=get_spouse(family, wife=False),
        wife=get_spouse(family, wife=True),
        children=get_field(family, "CHIL"),
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
        if family.wife and family.husband:
            individuals[family.wife].husband.add(family.husband)
            individuals[family.husband].wife.add(family.wife)

        for child in family.children:
            assert child in individuals, family
            assert (
                not individuals[child].mother
                or not family.wife
                or individuals[child].mother == family.wife
            ), [family, child, individuals[child]]
            assert (
                not individuals[child].father
                or not family.husband
                or individuals[child].father == family.husband
            ), [family, child, individuals[child]]
            individuals[child].mother = (
                family.wife if family.wife else individuals[child].mother
            )
            individuals[child].father = (
                family.husband if family.husband else individuals[child].father
            )

    return individuals
