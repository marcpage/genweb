#!/usr/bin/env python3


""" Hanldes loading and saving of metadta """


from glob import glob
from copy import deepcopy

from yaml import safe_load


def load_yaml(path: str) -> dict[str, dict]:
    """Loads a yaml file

    Args:
        path (str): The path to the yaml file

    Returns:
        dict[str, dict]: The data loaded from the yaml file
    """
    with open(path, "r", encoding="utf-8") as file:
        return safe_load(file)


class Metadata:
    """read-only-dict-like object"""

    def __init__(self, path: str):
        self.path = path
        self.original = Metadata.__load(path)
        self.updated = {}

    @staticmethod
    def __load(path_pattern: str) -> dict[str:dict]:
        result = {}

        for path in sorted(glob(path_pattern)):
            result.update(Metadata.__validate(load_yaml(path)))

        return result

    @staticmethod
    def __validate(metadata: dict[str:dict]) -> dict[str:dict]:
        return metadata

    def __combined(self, deep=False) -> dict[str:dict]:
        if deep:
            combined = deepcopy(self.original)
            combined.update(deepcopy(self.updated))
        else:
            combined = dict(self.original)
            combined.update(self.updated)

        return combined

    def __getitem__(self, key: str) -> dict:
        if key in self.updated:
            return deepcopy(self.updated[key])

        return deepcopy(self.original[key])

    def __repr__(self) -> str:
        return repr(self.__combined())

    def __len__(self) -> int:
        return len(self.__combined())

    def has_key(self, key: str) -> bool:
        """Is the given identifier available

        Args:
            key (str): The identifier

        Returns:
            bool: True if found
        """
        return key in self.original or key in self.updated

    def keys(self) -> list[str]:
        """A list of the identifiers

        Returns:
            list[str]: The identifiers
        """
        return self.__combined().keys()

    def values(self) -> list[dict]:
        """A list of the people

        Returns:
            list[dict]: The people
        """
        return [deepcopy(v) for v in self.__combined().values()]

    def items(self) -> list[tuple[str, dict]]:
        """Get a list of pairs of identifiers and people

        Returns:
            list[tuple(str, dict)]: The identifiers and people
        """
        return [(k, deepcopy(v)) for k, v in self.__combined().items()]

    def __contains__(self, key: str) -> bool:
        return key in self.original or key in self.updated

    def __iter__(self):
        return iter(self.__combined(deep=True))

    def get(self, key: str, default: dict | None = None) -> dict | None:
        """Gets the person for a given id, or a default person if the id is not found

        Args:
            key (str): The person's canonical identifier
            default (dict | None, optional): The person to return if the
                                                            id is not found. Defaults to None.

        Returns:
            dict | None: _description_
        """
        if key in self.updated:
            return deepcopy(self.updated[key])

        if key in self.original:
            return deepcopy(self.original[key])

        return default

    def __setitem__(self, key, item):
        self.updated[key] = item
