#!/usr/bin/env python3


""" This is the main website interface """


from os import makedirs, link, unlink, walk
from os.path import join, dirname, isfile, basename, relpath, commonpath
from shutil import copyfile
from shlex import quote
from sys import stdout

from devopsdriver.settings import Settings
from fabric import Connection

from genweb.relationships import load_gedcom
from genweb.people import People
from genweb.metadata import Metadata
from genweb.template import render_to_file
from genweb.inventory import Artifacts


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

        for person_id in info["people"]:
            if person_id not in people:
                PRINT(f"WARNING: person {person_id} missing for metadata {metadata_id}")
                continue

            people[person_id].metadata.append(metadata_id)


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


def copy_person_thumbnails(
    people: People, artifacts: Artifacts, dst_dir: str, default_thumbnail: str
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
        found = artifacts.paths(f"{person.id}.jpg")

        if not found:
            link(join(dst_dir, default_thumbnail), dest_file)
            continue

        if len(found) != 1:
            PRINT(f"WARNING: duplicate thumbnails for {person.id}")
            PRINT("\t" + "\n\t".join(found))

        link(join(artifacts.directory, found[0]), dest_file)
        artifacts.add(found[0])


def copy_metadata_files(
    artifacts: Artifacts,
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
    copy_list = metadata.get_copy_list(artifacts)

    for src_path, dst_path in copy_list:
        proposed_dst = join(dest_dir, dst_path)
        final_dst = destination_file(dirname(proposed_dst), basename(proposed_dst))
        link(join(artifacts.directory, src_path), final_dst)
        artifacts.add(src_path)

    copy_person_thumbnails(people, artifacts, dest_dir, default_thumbnail)


def metadata_references(metadata: dict[str, dict], artifacts: Artifacts):
    """Add references to any files that we haven't directly referenced yet

    Args:
        metadata (dict[str, dict]): The metadata to scan
        artifacts (Artifacts): The artifacts to update
    """
    for identifier, entry in metadata.items():
        if entry["type"] == "inline":  # add .src files that may exist
            found = artifacts.paths(entry["file"])
            artifacts.add(*found)

            if len(found) not in {0, 1}:
                print(f"WARNING: duplicate .src files for {identifier}")
                print("\t" + "\n\t".join(found))

        # add any .xml files that may exist
        found = artifacts.paths(f"{identifier}.xml")
        artifacts.add(*found)

        if len(found) not in {0, 1}:
            print(f"WARNING: duplicate .xml files for {identifier}")
            print("\t" + "\n\t".join(found))


def display_percent(item_index: int, items: list, last_percent: int) -> int:
    new_percent = int(100 * item_index / len(items))
    if new_percent <= last_percent:
        return last_percent

    stdout.write(".")
    stdout.flush()
    return new_percent


def copy_site(settings: Settings) -> None:
    # find Desktop -print -exec stat -f "'%Sm %z'" -t "%Y%m%d%H%M%S" "'{}'" "\;"
    # macOS
    if "remote_server" not in settings or "remote_path" not in settings:
        return

    elements = [e for e in walk(settings["site_dir"])]
    directories = sorted(
        [
            relpath(join(r, d), settings["site_dir"])
            for r, ds, _ in elements
            for d in ds
        ],
        key=len,
        reverse=True,
    )
    files = [
        relpath(join(r, f), settings["site_dir"]) for r, _, fs in elements for f in fs
    ]
    created_dirs = set()

    with Connection(settings["remote_server"]) as connection:

        print("Creating directories")
        last_percent = 0

        for dir_index, directory in enumerate(directories):
            if any(commonpath((directory, d)) == directory for d in created_dirs):
                continue

            remote_dir = join(settings["remote_path"], directory)
            result = connection.run(f"mkdir -p {quote(remote_dir)}")
            assert not result.stderr, result.stderr
            assert not result.stdout, result.stdout
            assert result.exited == 0, result.exited
            assert result.ok
            created_dirs.add(directory)
            last_percent = display_percent(dir_index, directories, last_percent)

        print("\nCopying files")
        last_percent = 0

        for file_index, file in enumerate(files):
            connection.put(
                join(settings["site_dir"], file), join(settings["remote_path"], file)
            )
            last_percent = display_percent(file_index, files, last_percent)


def main() -> None:
    """Generate the website"""
    settings = Settings(__file__)
    artifacts = Artifacts(settings["binaries_dir"])
    people = People(
        load_gedcom(settings["gedcom_path"]), settings.get("alias_path", None)
    )
    metadata = Metadata(settings["metadata_yaml"])
    link_people_to_metadata(people, metadata)
    copy_static_files(settings["copy files"], settings["site_dir"])
    copy_metadata_files(
        artifacts,
        settings["site_dir"],
        metadata,
        people,
        settings["unknown_thumbnail"],
    )
    generate_people_pages(settings["site_dir"], people, metadata)
    root_index_path = join(settings["site_dir"], "index.html")
    root_template_path = join(TEMPLATE_DIR, "top_level.html.mako")
    render_to_file(root_index_path, root_template_path, people=people)
    metadata_references(metadata, artifacts)
    copy_site(settings)
    # print("\n".join(f"WARNING: Not referenced: {f}" for f in artifacts.lost()))


if __name__ == "__main__":
    main()
