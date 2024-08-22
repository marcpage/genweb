#!/usr/bin/env python3


""" Hanldes loading and saving of metadta """


from glob import glob
from copy import deepcopy
from os.path import splitext, join, relpath
from datetime import datetime

from yaml import safe_load, safe_dump

from genweb.inventory import Artifacts


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
    """dict-like object
    When loading from file name.ext revisions are saved to name YYYY-MM-DD HH:MM:SS.ext
    Revisions saved earlier are preserved, but overridden by later revisions
    """

    def __init__(self, path: str):
        self.path = path  # original file

        # Calculate the file we will save any changes to
        base, extension = splitext(path)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.revision_path = f"{base} {now}{extension}"

        # load all the revisions
        self.original = Metadata.__load(path)
        self.updated = {}

    def save(self) -> None:
        """If there are changes saves them to the revision file"""
        if not self.updated:
            return

        with open(self.revision_path, "w", encoding="utf-8") as revision_file:
            safe_dump(self.updated, revision_file)

    @staticmethod
    def _inline_copy_list(inline: dict, artifacts: Artifacts) -> list[tuple[str, str]]:
        if "references" not in inline:
            return []

        found = []

        for referenced in inline["references"]:
            if not artifacts.has_file(referenced):
                continue  # TODO: handle in validate  # pylint: disable=fixme

            found.append((referenced, referenced))

        return found

    @staticmethod
    def _picture_copy_list(pict: dict, artifacts: Artifacts) -> list[tuple[str, str]]:
        picture_src = join(pict["path"], pict["file"])
        picture_dst = join(pict["path"], pict["file"])
        found = []

        if not artifacts.has_file(picture_src):
            return []  # TODO: handle in validate pict  # pylint: disable=fixme

        found.append((picture_src, picture_dst))

        if not "original" in pict:
            return found

        original_src = join(pict["path"], pict["original"])
        original_dst = join(pict["path"], pict["original"])

        if not artifacts.has_file(original_src):
            return found  # TODO: handle in validate pict  # pylint: disable=fixme

        found.append((original_src, original_dst))

        return found

    @staticmethod
    def _href_copy_list(href: dict, artifacts: Artifacts) -> list[tuple[str, str]]:
        href_src = join(href["path"], href["folder"])
        href_dst = join(href["path"], href["folder"])

        if not artifacts.has_dir(href_src):
            return []  # TODO: handle in validate href  # pylint: disable=fixme

        if not artifacts.has_file(join(href_src, href["file"])):
            return []  # TODO: handle in validate href  # pylint: disable=fixme

        return [
            (file, join(href_dst, relpath(file, href_src)))
            for file in artifacts.files_under(href_src)
        ]

    def get_copy_list(self, artifacts: Artifacts) -> list[tuple[str, str]]:
        """Get the list of relative source and destination paths referenced in metadata

        Args:
            artifacts (Artifacts): The artifacts to look for files

        Returns:
            list[tuple[str, str]]: List of relative source and destination path pairs
        """
        to_copy = []
        call = {
            "href": Metadata._href_copy_list,
            "picture": Metadata._picture_copy_list,
            "inline": Metadata._inline_copy_list,
        }

        for item in self.values():
            assert item["type"] in call, f"unknown type {item['type']}"
            to_copy.extend(call[item["type"]](item, artifacts))

        return to_copy

    @staticmethod
    def __load(path: str) -> dict[str:dict]:
        result = {}

        # Revisions are stored as: base YYYY-mm-dd HH:MM:SS.ext
        base, extension = splitext(path)
        revisions = glob(base + "*" + extension)
        # ensure we load the original file first
        revisions.remove(path)
        revisions.sort()
        revisions.insert(0, path)

        # load them in order to have later override earlier
        for revision_path in revisions:
            revision = Metadata.__validate(load_yaml(revision_path))
            result.update(revision)
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

    # MARK: dict methods

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
