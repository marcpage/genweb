#!/usr/bin/env python3

""" Parse the xml data files """

from xml.etree.ElementTree import parse, ParseError
from os import walk
from os.path import join, splitext
from platform import system
from sys import exit as return_code

from yaml import dump
from devopsdriver.settings import Settings


PRINT = print
RETURN_CODE = return_code


def read_xml(path: str) -> dict:
    """reads and sanitizes an xml file

    Args:
        path (str): path to the xml file

    Returns:
        dict: the contents of the xml file as a dictionary
    """
    doc = parse(path)
    root = doc.getroot()
    nodes = {n.tag for n in root}
    result = {
        k: root.findall(k)[0].text.strip() if root.findall(k)[0].text else None
        for k in nodes
    }
    result["type"] = root.tag
    assert all(len(root.findall(k)) == 1 for k in nodes), f"Duplicate tags in {path}"
    result["width"] = int(result["width"]) if result.get("width", None) else None
    result["height"] = int(result["height"]) if result.get("height", None) else None
    result["people"] = (
        result["people"].split(";") if result.get("people", None) else None
    )
    return {k: v for k, v in result.items() if v}


def validate_settings(settings: Settings):
    """Validates that enough settings have been set.
        If not all Settings have been set, then prints error message and exits with non-zero code.

    Args:
        settings (Settings): The settings to check
    """
    if "xmldir" not in settings:
        PRINT("ERROR: Please make sure you add xmldir, srcdir, and finalyaml to:")
        PRINT(
            "\t"
            + Settings.PREF_DIR.get(
                system(), Settings.PREF_DIR[Settings.DEFAULT_PREF_DIR]
            )
            + "/parse_metadata.yml"
        )
        RETURN_CODE(1)


def load_metadata(search_dir: str) -> dict[str, dict]:
    """Searchs a directory for XML files to load

    Returns:
        dict[str:dict]: The metadata
    """
    metadata = {}

    for root, _, files in walk(search_dir):
        for file in [f for f in files if splitext(f)[1].lower() == ".xml"]:
            try:
                metadata[splitext(file)[0]] = read_xml(join(root, file))

            except (ParseError, IndexError, AssertionError) as error:
                PRINT(f"{join(root, file)}: {error}")

    return metadata


def load_inlines(metadata: dict[str, dict], src_search_dir: str):
    """Loads .src file contents directly into the metadata

    Args:
        metadata (dict[str, dict]): The metadata to update
        src_search_dir (str): The directory to search for .src files
    """
    existing_files = {f: join(r, f) for r, _, fs in walk(src_search_dir) for f in fs}

    for entry in metadata.values():
        if entry["type"] == "inline":
            if entry["file"] not in existing_files:
                PRINT(f"WARNING: inline src missing: {entry['file']}")
                continue

            with open(existing_files[entry["file"]], "r", encoding="utf-8") as source:
                entry["contents"] = source.read()


def main() -> None:
    """searches for xml files and merges into yml file"""
    settings = Settings(__file__)
    validate_settings(settings)
    metadata = load_metadata(settings["xmldir"])
    load_inlines(metadata, settings["srcdir"])

    with open(settings["finalyaml"], "w", encoding="utf-8") as file:
        dump(metadata, file)


if __name__ == "__main__":
    main()
