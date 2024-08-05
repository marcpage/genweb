#!/usr/bin/env python3

""" Parse the xml data files """

from xml.etree.ElementTree import parse, ParseError
from os import walk, unlink
from os.path import join, splitext


KNOWN_TAGS = {
    "path",
    "file",
    "title",
    "comment",
    "people",
    "mod_date",
    "width",
    "height",
    "caption",
    "folder",
    "href",
}


def read_xml(path: str) -> dict:
    doc = parse(path)
    root = doc.getroot()
    nodes = {n.tag for n in root}
    assert not nodes - KNOWN_TAGS, nodes - KNOWN_TAGS
    assert root.tag in {"inline", "picture", "comment"}, root.tag
    return {
        k: root.findall(k)[0].text
        for k in ["path", "file", "title", "comment", "people"]
    }


def main() -> None:
    for root, _, files in walk("/Users/marcp/Desktop/metadata"):
        for file in [f for f in files if splitext(f)[1].lower() == ".xml"]:
            try:
                _ = read_xml(join(root, file))

            except (ParseError, IndexError, AssertionError) as error:
                with open(join(root, file), "r", encoding="utf-8") as contents:
                    pass  # print(contents.read())

                if "mismatch" in str(error):
                    print(join(root, file))
                    print(error)
                    print("=" * 80)


if __name__ == "__main__":
    main()
