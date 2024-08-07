#!/usr/bin/env python3

""" This is the main website interface """

from os import makedirs
from os.path import join, dirname
from devopsdriver.settings import Settings

from genweb.relationships import load_gedcom
from genweb.people import People
from genweb.metadata import load_yaml
from genweb.template import render

TEMPLATE_DIR = join(dirname(__file__), "templates")


def link_people_to_metadata(people: People, metadata: dict[str, dict]) -> None:
    """puts metadata identifir=ers in the appropriate people

    Args:
        people (People): the database of people
        metadata (dict[str, dict]): database of metadata
    """
    for metadata_id, info in metadata.items():
        if "people" not in info:
            print(f"WARNING: no info for metadata {metadata_id}")
            continue
        for personid in info["people"]:
            if personid not in people:
                print(f"WARNING: person {personid} missing for metadata {metadata_id}")
                continue
            people[personid].metadata.append(metadata_id)


def main() -> None:
    """Generate the website"""
    settings = Settings(__file__)
    people = People(load_gedcom(settings["gedcom_path"]))
    metadata = load_yaml(settings["metadata_yaml"])
    link_people_to_metadata(people, metadata)
    site_dir = settings["site_dir"]
    metadata_people = [p for p in people.values() if p.metadata]
    template_path = join(TEMPLATE_DIR, "person.html.mako")
    for person in metadata_people:
        person_dir = join(site_dir, person.id)
        makedirs(person_dir, exist_ok=True)
        index_path = join(person_dir, "index.html")
        contents = render(template_path, person=person, people=people)
        with open(index_path, "w", encoding="utf-8") as index_file:
            index_file.write(contents)
    root_index_path = join(site_dir, "index.html")
    root_template_path = join(TEMPLATE_DIR, "top_level.html.mako")
    root_contents = render(root_template_path, people=people)
    with open(root_index_path, "w", encoding="utf-8") as index_file:
        index_file.write(root_contents)


if __name__ == "__main__":
    main()
