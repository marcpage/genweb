#!/usr/bin/env python3

""" Parse the xml data files """

from xml.etree.ElementTree import parse, ParseError
from os import walk
from os.path import join, splitext, isfile, normpath
from platform import system
from sys import exit as return_code
from re import compile as regex, DOTALL

from yaml import dump
from devopsdriver.settings import Settings


PRINT = print
RETURN_CODE = return_code
PATH_PATTERN = regex(
    r'<(a|img|source)[^>]+(src|alt|href|background|name|title)="([^"]+)"', DOTALL
)
INVALID_PATTERN = regex(r"^(#|https?://|mailto:)")
VALID_EXTENSIONS = {
    ".epub",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
}


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
                element = read_xml(join(root, file))
                assert isinstance(element, dict), "Not an object"
                assert "type" in element, "No type field"
                assert element["type"] in {
                    "picture",
                    "inline",
                    "href",
                }, f"Unknown type: {element['type']}"
                metadata[splitext(file)[0]] = element

            except (ParseError, IndexError, AssertionError) as error:
                PRINT(f"{join(root, file)}: {error}")

    return metadata


def load_picture(entry: dict, src_search_dir: str):
    """Looks for an original file ("+" prefix) and adds "original" key

    Args:
        entry (dict): The picture description
        src_search_dir (str): The directory to search for the original file
    """
    if entry["type"] != "picture":
        return

    original_path = join(src_search_dir, entry["path"], "+" + entry["file"])

    if not isfile(original_path):
        return

    entry["original"] = "+" + entry["file"]


def load_references(entry: dict):
    """Parses the inline html for files that are expected to be
           in the website.

    Args:
        entry (dict): The inline entry
        src_search_dir (str): The directory to search for files
    """
    if "contents" not in entry or entry["type"] != "inline":
        return

    entry["references"] = [
        normpath(join(entry["path"], m.group(3).strip()))
        for m in PATH_PATTERN.finditer(entry["contents"])
        if not INVALID_PATTERN.match(m.group(3).strip())
        and splitext(m.group(3))[1].lower() in VALID_EXTENSIONS
    ]


def load_inline(entry: dict, src_search_dir: str, identifier: str):
    """Load the .src file for an inline and add references

    Args:
        entry (dict): The inline item to add
        src_search_dir (str): The directory to load .src file from
    """
    if entry["type"] != "inline":
        return

    if "path" not in entry:
        print(f"WARNING: inline path missing for {identifier}")
        return

    src_path = join(src_search_dir, entry["path"], entry["file"])

    if not isfile(src_path):
        PRINT(f"WARNING: inline src file not found for {identifier}: {src_path}")
        return

    with open(src_path, "r", encoding="utf-8") as source:
        entry["contents"] = source.read()

    load_references(entry)


def load_external(metadata: dict[str, dict], src_search_dir: str):
    """Loads .src file contents directly into the metadata

    Args:
        metadata (dict[str, dict]): The metadata to update
        src_search_dir (str): The directory to search for .src files
    """
    for identifier, entry in metadata.items():
        load_inline(entry, src_search_dir, identifier)
        load_picture(entry, src_search_dir)


def main() -> None:
    """searches for xml files and merges into yml file"""
    settings = Settings(__file__)
    validate_settings(settings)
    metadata = load_metadata(settings["xmldir"])
    load_external(metadata, settings["srcdir"])

    with open(settings["finalyaml"], "w", encoding="utf-8") as file:
        dump(metadata, file)


if __name__ == "__main__":
    main()
