#!/usr/bin/env python3


""" This is the main website interface """


from os import makedirs, link
from os.path import join, dirname
from devopsdriver.settings import Settings

from genweb.relationships import load_gedcom
from genweb.people import People
from genweb.metadata import load_yaml
from genweb.template import render_to_file


TEMPLATE_DIR = join(dirname(__file__), "templates")
PRINT = print


def link_people_to_metadata(people: People, metadata: dict[str, dict]) -> None:
    """puts metadata identifir=ers in the appropriate people

    Args:
        people (People): the database of people
        metadata (dict[str, dict]): database of metadata
    """
    for metadata_id, info in metadata.items():
        if "people" not in info:
            PRINT(f"WARNING: no info for metadata {metadata_id}")
            continue
        for personid in info["people"]:
            if personid not in people:
                PRINT(f"WARNING: person {personid} missing for metadata {metadata_id}")
                continue
            people[personid].metadata.append(metadata_id)


def generate_people_pages(
    site_dir: str, people: People, metadata: dict[str, dict]
) -> None:
    """Generates a page for each person with metadata

    Args:
        site_dir (str): The path to the site directory
        people (People): The people to possibly generate pages for
    """
    metadata_people = [p for p in people.values() if p.metadata]
    template_path = join(TEMPLATE_DIR, "person.html.mako")

    for person in metadata_people:
        person_dir = join(site_dir, person.id)
        makedirs(person_dir, exist_ok=True)
        index_path = join(person_dir, "index.html")
        render_to_file(
            index_path, template_path, person=person, people=people, metadata=metadata
        )


def copy_static_files(files: dict[str, str], destination: str) -> None:
    """Copy any static files from the repo to the website

    Args:
        files (dict[str, str]): List of relative paths (dest->source) to copy
        destination (str): website directory root
    """
    source_dir = dirname(__file__)

    for dest_path, source_path in files.items():
        destination_path = join(destination, dest_path)
        makedirs(dirname(destination_path), exist_ok=True)
        link(join(source_dir, source_path), destination_path)


def main() -> None:
    """Generate the website"""
    settings = Settings(__file__)
    people = People(load_gedcom(settings["gedcom_path"]))
    metadata = load_yaml(settings["metadata_yaml"])
    link_people_to_metadata(people, metadata)
    copy_static_files(settings["copy files"], settings["site_dir"])
    generate_people_pages(settings["site_dir"], people, metadata)
    root_index_path = join(settings["site_dir"], "index.html")
    root_template_path = join(TEMPLATE_DIR, "top_level.html.mako")
    render_to_file(root_index_path, root_template_path, people=people)


if __name__ == "__main__":
    main()
