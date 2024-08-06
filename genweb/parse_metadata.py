#!/usr/bin/env python3

""" Parse the xml data files """

from xml.etree.ElementTree import parse, ParseError
from os import walk
from os.path import join, splitext
from platform import system
from sys import exit as return_code

from yaml import dump
from devopsdriver.settings import Settings


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
    result = {k: root.findall(k)[0].text for k in nodes}
    result["type"] = root.tag
    assert all(len(root.findall(k)) == 1 for k in nodes), path

    result["width"] = int(result["width"]) if result.get("width", None) else None
    result["height"] = int(result["height"]) if result.get("height", None) else None
    result["people"] = (
        result["people"].split(";") if result.get("people", None) else None
    )
    return {k: v for k, v in result.items() if v}


def main() -> None:
    """searches for xml files and merges into yml file"""
    metadata = {}
    settings = Settings(__file__)

    if "xmldir" not in settings:
        print("ERROR: Please make sure you add xmldir, srcdir, and finalyaml to:")
        print(
            "\t"
            + Settings.PREF_DIR.get(
                system(), Settings.PREF_DIR[Settings.DEFAULT_PREF_DIR]
            )
            + "/parse_metadata.yml"
        )
        return_code(1)

    for root, _, files in walk(settings["xmldir"]):
        for file in [f for f in files if splitext(f)[1].lower() == ".xml"]:
            try:
                metadata[splitext(file)[0]] = read_xml(join(root, file))

            except (ParseError, IndexError, AssertionError) as error:
                print(join(root, file))
                print(error)

    for entry in metadata.values():
        if entry["type"] == "inline":
            pass

    with open(settings["finalyaml"], "w", encoding="utf-8") as file:
        dump(metadata, file)


if __name__ == "__main__":
    main()
