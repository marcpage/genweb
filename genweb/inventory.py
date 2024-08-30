#!/usr/bin/env python3


""" Keep track of artifact files """


from os import walk, stat, makedirs
from os.path import join, relpath, isfile, basename, commonpath
from types import SimpleNamespace
from hashlib import new as Hasher
from json import load, dump


class Artifacts:
    """keep track of files used and unused"""

    HASH_FILE_CHUNK_SIZE_BYTES = 1 * 1024 * 1024  # 1 MiB

    def __init__(self, directory: str, cache_dir: str = None):
        self.cache_dir = cache_dir if cache_dir else join(directory, "metadata")
        self.directory = directory
        self.inventory = {}
        self.refresh()
        self._load_cache()

    @staticmethod
    def _new_entry(**kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            size=kwargs.get("size", None),
            modified=kwargs.get("modified", None),
            hash=kwargs.get("hash", None),
            accounted=kwargs.get("accounted", False),
        )

    def _cache_path(self) -> str:
        return join(self.cache_dir, "artifact hash cache.json")

    def _load_cache(self) -> None:
        cache_path = self._cache_path()

        if not isfile(cache_path):
            return

        with open(cache_path, "r", encoding="utf-8") as cache_file:
            cached = load(cache_file)

        for path, info in cached.items():
            if path in self.inventory:
                self.inventory[path].modified = info.get("modified", None)
                self.inventory[path].size = info.get("size", None)
                self.inventory[path].hash = info.get("hash", None)

    def _save_cache(self) -> None:
        cache_data = {
            p: {"modified": i.modified, "size": i.size, "hash": i.hash}
            for p, i in self.inventory.items()
            if i.modified and i.hash and i.size is not None
        }
        makedirs(self.cache_dir, exist_ok=True)

        with open(self._cache_path(), "w", encoding="utf-8") as cache_file:
            dump(cache_data, cache_file)

    @staticmethod
    def _hash_file(path: str) -> str:
        hasher = Hasher("sha256")

        with open(path, "rb") as contents:
            while True:
                block = contents.read(Artifacts.HASH_FILE_CHUNK_SIZE_BYTES)

                if not block:
                    break

                hasher.update(block)

        return hasher.hexdigest()

    @staticmethod
    def _hash_valid(path: str, entry: SimpleNamespace) -> bool:
        if entry.size is None or not entry.modified or not entry.hash:
            return False

        file_info = stat(path)

        if file_info.st_size != entry.size:
            return False

        if file_info.st_mtime != entry.modified:
            return False

        return True

    @staticmethod
    def _update_stat(entry: SimpleNamespace, path: str):
        file_info = stat(path)
        entry.size = file_info.st_size
        entry.modified = file_info.st_mtime

    def hash(self, path: str) -> str:
        """Gets the hash of the given file.
            Hashes are cached along with mdoficiation timestamp and size.
            If the size and modification timestamp from the cache match
            the file, the cached hash is returned.
            If the file has been modified since the hash was generated,
            a new hash is generated and cached.

        Args:
            path (str): The relative path of the file

        Returns:
            str: The sha256 hash hex digest of the contents of the file
        """
        full_path = join(self.directory, path)
        assert isfile(full_path), full_path
        self.inventory[path] = self.inventory.get(
            path,
            Artifacts._new_entry(),
        )
        entry = self.inventory[path]

        if not Artifacts._hash_valid(full_path, entry):
            entry.hash = Artifacts._hash_file(full_path)
            Artifacts._update_stat(entry, full_path)
            self._save_cache()

        return entry.hash

    def _populate_all_stats(self):
        """42,787 files in 0.05 - 0.06 seconds on MacBook Pro M2"""
        no_size = [p for p, i in self.inventory.items() if i.size is None]

        for path in no_size:
            Artifacts._update_stat(self.inventory[path], join(self.directory, path))

    def get_files_of_size(self, size: int) -> list[str]:
        """Finds all files with a given file size

        Args:
            size (int): The number of bytes in the file(s) we're looking for

        Returns:
            list[str]: The list of relative paths to the files with that size
        """
        self._populate_all_stats()
        return [p for p, i in self.inventory.items() if i.size == size]

    def lookup_hashes(self, hash_sizes: dict[str, int]) -> dict[str, list[str]]:
        """Given a list of hashes and the file size it represents, get the list of paths.
            The size is an optimization to prevent the need to hash every file.

        Args:
            hash_sizes (dict[str, int]): Map of hash to filesize

        Returns:
            dict[str, list[str]]: Map of hash to list of relative paths that match that hash
        """
        return {
            h: [p for p in self.get_files_of_size(s) if self.hash(p) == h]
            for h, s in hash_sizes.items()
        }

    def refresh(self) -> None:
        """Looks for new files in the artifacts directory"""
        all_files = {
            relpath(join(r, f), self.directory)
            for r, _, fs in walk(self.directory)
            for f in fs
        }

        for file in all_files:
            if file not in self.inventory:
                self.inventory[file] = Artifacts._new_entry()

    def paths(self, filename: str) -> list[str]:
        """Returns all the paths for a given filename

        Args:
            filename (str): The filename to search

        Returns:
            list[str]: The list of relative paths from the artifacts directory for
                            all files found with that filename
        """
        return [f for f in self.inventory if basename(f) == filename]

    def suffixed(self, suffix: str) -> list[str]:
        """Finds all relative file paths that end with the given suffix

        Args:
            suffix (str): The end of the path to look for (may include path separators)

        Returns:
            list[str]: The list of relative paths that end with the given suffix
        """
        return [f for f in self.inventory if f.endswith(suffix)]

    def has_file(self, file_path: str) -> bool:
        """See if this file exists

        Args:
            file_path (str): The file to check

        Returns:
            bool: Does it exist
        """
        return file_path in self.inventory

    def has_dir(self, dir_path: str) -> bool:
        """Does a directory with a file in it exist

        Args:
            dir_path (str): The directory

        Returns:
            bool: We found the directory (must have a file in it)
        """
        return any(commonpath([dir_path, f]) == dir_path for f in self.inventory)

    def files_under(self, dir_path: str) -> list[str]:
        """Get the list of files in a directory (recursively)

        Args:
            dir_path (str): The directory to search

        Returns:
            list[str]: The files under that directory
        """
        return [f for f in self.inventory if commonpath([dir_path, f]) == dir_path]

    def add(self, *relative_file_path: str) -> None:
        """Adds a file to the inventory

        Args:
            relative_file_path (str): Files to add
        """
        not_found = []

        for path in relative_file_path:
            if path not in self.inventory and isfile(join(self.directory, path)):
                self.inventory[path] = Artifacts._new_entry(accounted=True)
                continue

            if path not in self.inventory:
                not_found.append(path)
                continue

            self.inventory[path].accounted = True

        assert len(not_found) == 0, not_found

    def lost(self) -> list[str]:
        """Gets a list of all the files in the artifacts directory that have not been referenced

        Returns:
            set[str]: All unreferenced files
        """
        return [p for p, i in self.inventory.items() if not i.accounted]
