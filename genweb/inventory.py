#!/usr/bin/env python3


""" Keep track of artifact files """


from os import walk
from os.path import join, relpath, isfile, basename, commonpath


class Artifacts:
    """keep track of files used and unused"""

    def __init__(self, directory: str):
        self.directory = directory
        self.accounted = set()
        self.unaccounted = set()
        self.refresh()

    def refresh(self):
        """Looks for new files in the artifacts directory"""
        all_files = {
            relpath(join(r, f), self.directory)
            for r, _, fs in walk(self.directory)
            for f in fs
        }
        self.unaccounted = all_files - self.accounted

    def paths(self, filename: str) -> list[str]:
        """Returns all the paths for a given filename

        Args:
            filename (str): The filename to search

        Returns:
            list[str]: The list of relative paths from the artifacts directory for
                            all files found with that filename
        """
        return [f for f in self.accounted | self.unaccounted if basename(f) == filename]

    def suffixed(self, suffix: str) -> list[str]:
        """Finds all relative file paths that end with the given suffix

        Args:
            suffix (str): The end of the path to look for (may include path separators)

        Returns:
            list[str]: The list of relative paths that end with the given suffix
        """
        return [f for f in self.accounted | self.unaccounted if f.endswith(suffix)]

    def has_file(self, file_path: str) -> bool:
        """See if this file exists

        Args:
            file_path (str): The file to check

        Returns:
            bool: Does it exist
        """
        return file_path in self.unaccounted or file_path in self.accounted

    def has_dir(self, dir_path: str) -> bool:
        """Does a directory with a file in it exist

        Args:
            dir_path (str): The directory

        Returns:
            bool: We found the directory (must have a file in it)
        """
        return any(
            commonpath([dir_path, f]) == dir_path
            for f in self.accounted | self.unaccounted
        )

    def files_under(self, dir_path: str) -> list[str]:
        """Get the list of files in a directory (recursively)

        Args:
            dir_path (str): The directory to search

        Returns:
            list[str]: The files under that directory
        """
        return [
            f
            for f in self.accounted | self.unaccounted
            if commonpath([dir_path, f]) == dir_path
        ]

    def add(self, *relative_file_path: str):
        """Adds a file to the inventory

        Args:
            relative_file_path (str): Files to add
        """
        for path in relative_file_path:
            if path in self.accounted:
                continue

            assert path in self.unaccounted or isfile(join(self.directory, path)), path
            self.accounted.add(path)

            if path in self.unaccounted:
                self.unaccounted.remove(path)

    def lost(self) -> set[str]:
        """Gets a list of all the files in the artifacts directory that have not been referenced

        Returns:
            set[str]: All unreferenced files
        """
        return set(self.unaccounted)
