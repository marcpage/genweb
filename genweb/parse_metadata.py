#!/usr/bin/env python3

""" Parse the xml data files """

from xml.etree.ElementTree import parse, ParseError
from os import walk
from os.path import join, splitext
from yaml import dump


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

    for root, _, files in walk("/home/pagerk/metadata/xml"):
        for file in [f for f in files if splitext(f)[1].lower() == ".xml"]:
            try:
                metadata[splitext(file)[0]] = read_xml(join(root, file))

            except (ParseError, IndexError, AssertionError) as error:
                print(join(root, file))
                print(error)
    with open("metadata.yml", "w", encoding="utf-8") as file:
        dump(metadata, file)

if __name__ == "__main__":
    main()
