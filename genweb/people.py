#!/usr/bin/env python3


""" Information about the people """


from types import SimpleNamespace
from re import compile as regex

from genweb.metadata import load_yaml


WHITESPACE = regex(r"\s+")
PRINT = print


class People:
    """A read-only dictionary like object that maps identifier to people"""

    def __init__(self, people: dict[str, SimpleNamespace], alias_path: str):
        self.aliases = load_yaml(alias_path) if alias_path else {}
        self.by_id = self._remap(people, self.aliases)

    def cannonical_id(self, identifier: str) -> str:
        """Looks up the canonical identifier

        Args:
            identifier (str): The (possibly) not canonical identifier

        Returns:
            str: The canonical identifier or the original identifier if it is cnanonical or unknown
        """
        if identifier in self.by_id:
            return identifier

        return People._fix_id(identifier, self.aliases)

    @staticmethod
    def _fix_id(identifier: str, aliases: dict[str : list[str]]) -> str:
        """Given an identifier, sees if it is an alias and returns the canonical

        Args:
            identifier (str): Possibly not canonical identifier
            aliases (_type_): Mapping of canonical identifiers ot potential aliases

        Returns:
            str: The canonical idenitifer or the original identifier if it is not a known alias
        """
        if identifier in aliases:
            return identifier

        possible = [
            i for i, aliases in aliases.items() for a in aliases if a == identifier
        ]
        assert len(possible) in {0, 1}, identifier
        return possible[0] if possible else identifier

    @staticmethod
    def _format_person(person: SimpleNamespace) -> str:
        """creates the person identifier

        Args:
            person (SimpleNamespace): the person to format

        Returns:
            str: the partial canonical identifier
        """
        if person is None:
            return "-"

        given_names = WHITESPACE.split(person.given.strip())
        first = given_names[0]
        middle = given_names[1][0] if len(given_names) > 1 else ""
        year = "0000" if person.birthdate is None else person.birthdate.strftime("%Y")
        return f"{person.surname}{first}{middle}{year}"

    @staticmethod
    def _identifier(person: SimpleNamespace, mother: SimpleNamespace | None) -> str:
        """Generates a canonical identifier given a person and their mother

        Args:
            person (SimpleNamespace): The person to generate the id for
            mother (SimpleNamespace | None): The person's mother

        Returns:
            str: The canonical identifier for the person
        """
        return People._format_person(person) + People._format_person(mother)

    @staticmethod
    def _find_mother(
        person: SimpleNamespace, people: dict[str, SimpleNamespace]
    ) -> SimpleNamespace | None:
        """Given a person look up the female parent

        Args:
            person (SimpleNamespace): The person to look at
            people (dict[str, SimpleNamespace]): The list of people by id

        Returns:
            SimpleNamespace | None: Either the single female parent or None if none found
        """
        mothers = [people[i] for i in person.parents if people[i].gender == "F"]

        if len(mothers) > 1:
            PRINT(f"WARNING: found multiple mothers for {person}")
            PRINT("\t" + "\n\t".join(str(m) for m in mothers))
            mothers = [m for m in mothers if m.surname != person.surname]
            PRINT(f"using: {mothers[0]}")

        return mothers[0] if mothers else None

    @staticmethod
    def _remap(
        people: dict[str, SimpleNamespace], aliases: dict[str : list[str]]
    ) -> dict[str, SimpleNamespace]:
        """Given a map of old id to people, remap them to canonical id to people and fix links

        Args:
            people (dict[str, SimpleNamespace]): All people mapped by old id's

        Returns:
            dict[str, SimpleNamespace]: Map of new id's to people whose internal id's
                                            have been updated
        """

        # Calculate mapping of old id's to new id's
        id_mapping = {
            p.id: People._fix_id(
                People._identifier(p, People._find_mother(p, people)), aliases
            )
            for p in people.values()
        }

        # now update id's for children, parents, and spouses
        for person in people.values():
            person.id = id_mapping[person.id]
            person.children = {id_mapping[i] for i in person.children}
            person.parents = {id_mapping[i] for i in person.parents}
            person.spouses = {id_mapping[i] for i in person.spouses}

        return {p.id: p for p in people.values()}

    def __getitem__(self, key: str) -> SimpleNamespace:
        return self.by_id[self.cannonical_id(key)]

    def __repr__(self) -> str:
        return repr(self.by_id)

    def __len__(self) -> int:
        return len(self.by_id)

    def has_key(self, key: str) -> bool:
        """Is the given identifier available

        Args:
            key (str): The identifier

        Returns:
            bool: True if found
        """
        return self.cannonical_id(key) in self.by_id

    def keys(self) -> list[str]:
        """A list of the identifiers

        Returns:
            list[str]: The identifiers
        """
        return self.by_id.keys()

    def values(self) -> list[SimpleNamespace]:
        """A list of the people

        Returns:
            list[SimpleNamespace]: The people
        """
        return self.by_id.values()

    def items(self) -> list[tuple[str, SimpleNamespace]]:
        """Get a list of pairs of identifiers and people

        Returns:
            list[tuple(str, SimpleNamespace)]: The identifiers and people
        """
        return self.by_id.items()

    def __contains__(self, key: str) -> bool:
        return self.cannonical_id(key) in self.by_id

    def __iter__(self):
        return iter(self.by_id)

    def get(
        self, key: str, default: SimpleNamespace | None = None
    ) -> SimpleNamespace | None:
        """Gets the person for a given id, or a default person if the id is not found

        Args:
            key (str): The person's canonical identifier
            default (SimpleNamespace | None, optional): The person to return if the
                                                            id is not found. Defaults to None.

        Returns:
            SimpleNamespace | None: _description_
        """
        return self.by_id.get(self.cannonical_id(key), default)
