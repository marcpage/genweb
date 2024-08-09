#!/usr/bin/env python3


""" This is the main website interface """


from os import makedirs, link, walk, unlink
from os.path import join, dirname, isfile, relpath
from shutil import copyfile

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
        copyfile(join(source_dir, source_path), destination_path)


def destination_file(dst_dir: str, filename: str) -> str:
    """Given a root directory, subdirectory, and filename, ensure we can link a file there

    Args:
        dst_dir (str): The root directory
        filename (str): The filename that will be created

    Returns:
        str: The path to the file that can now be linked
    """
    makedirs(dst_dir, exist_ok=True)
    dest_file = join(dst_dir, filename)

    if isfile(dest_file):
        unlink(dest_file)

    return dest_file


def copy_metadata_pictures(
    metadata: dict[str, dict],
    existing_files: dict[str, str],
    src_dir: str,
    dst_dir: str,
) -> None:
    """Copy all the picture metadata from a source directory to its destination

    Args:
        metadata (dict[str, dict]): The metadata description
        existing_files (dict[str, str]): Map of filename to absolute path to that file in src_dir
        src_dir (str): The source directory
        dst_dir (str): The destination directory (website)
    """
    for item in metadata.values():
        if item["type"] != "picture":
            continue

        if item["file"] not in existing_files:
            PRINT(f'WARNING: {item["file"]} not found in {src_dir}')
            continue

        dest_file = destination_file(join(dst_dir, item["path"]), item["file"])
        link(existing_files[item["file"]], dest_file)


def copy_person_thumbnails(
    people: People, existing_files: dict[str, str], dst_dir: str, default_thumbnail: str
) -> None:
    """Copy each person's thumbnail to the website or use the default

    Args:
        people (People): The people to evaluate
        existing_files (dict[str, str]): Map of names of all files in the source to
                                            their absolute path
        dst_dir (str): The destination directory (website)
        default_thumbnail (str): The path to the default thumbnail to use if the person does
                                    not have one
    """
    for person in people.values():
        if not person.metadata:
            continue

        dest_file = destination_file(join(dst_dir, person.id), f"{person.id}.jpg")

        if f"{person.id}.jpg" not in existing_files:
            PRINT(f"WARNING: no thumbnail for {person.id}")
            link(join(dst_dir, default_thumbnail), dest_file)
            continue

        link(existing_files[f"{person.id}.jpg"], dest_file)


def copy_metadata_hrefs(
    metadata: dict[str, dict],
    src_dir: str,
    dst_dir: str,
) -> None:
    """copy the href dirs

    Args:

        metadata (dict[str, dict]): The metadata description
        src_dir (str): The source directory
        dst_dir (str): The destination directory (website)
    """
    for item in metadata.values():
        if item["type"] != "href":
            continue
        hrefsource = join(src_dir, item["path"], item["folder"])
        if not isfile(join(hrefsource, item["file"])):
            PRINT(f'WARNING: {item["file"]} not found in {hrefsource}')
            continue

        hrefdest = join(dst_dir, item["path"], item["folder"])
        for root, _, files in walk(hrefsource):
            relativeroot = relpath(root, hrefsource)
            for file in files:
                sourcefile = join(root, file)
                dest_file = destination_file(join(hrefdest, relativeroot), file)

                link(sourcefile, dest_file)


def copy_metadata_files(
    sourcedir: str,
    dest_dir: str,
    metadata: dict[str, dict],
    people: People,
    default_thumbnail: str,
) -> None:
    """copy metadata files from source to website

    Args:
        sourcedir (str): location of original files
        dest_dir (str): location of website
        metadata (dict[str, dict]): _description_
    """
    existing_files = {f: join(r, f) for r, _, fs in walk(sourcedir) for f in fs}
    copy_metadata_pictures(metadata, existing_files, sourcedir, dest_dir)
    copy_metadata_hrefs(metadata, sourcedir, dest_dir)
    copy_person_thumbnails(people, existing_files, dest_dir, default_thumbnail)


def main() -> None:
    """Generate the website"""
    settings = Settings(__file__)
    people = People(load_gedcom(settings["gedcom_path"]))
    metadata = load_yaml(settings["metadata_yaml"])
    link_people_to_metadata(people, metadata)
    copy_static_files(settings["copy files"], settings["site_dir"])
    copy_metadata_files(
        settings["binaries_dir"],
        settings["site_dir"],
        metadata,
        people,
        settings["unknown_thumbnail"],
    )
    generate_people_pages(settings["site_dir"], people, metadata)
    root_index_path = join(settings["site_dir"], "index.html")
    root_template_path = join(TEMPLATE_DIR, "top_level.html.mako")
    render_to_file(root_index_path, root_template_path, people=people)


if __name__ == "__main__":
    main()
