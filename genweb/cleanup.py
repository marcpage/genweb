#!/usr/bin/env python3


""" Ensures artifacts directory is in a clean state

Because I have a zipped copy of the FamilyHistoryWeb directory, I am having to fix
these things every time. This script allows me to automatically clean up from
the snapshot I took. It should be safe to run at any point.

"""


from os import makedirs, walk
from os.path import join, basename, dirname, exists, splitext, relpath
from sys import argv
from platform import system as os_system
from shutil import move
from functools import cache
from re import compile as regex, DOTALL

from devopsdriver.settings import Settings, load_yaml


DRY_RUN = "-n" in argv


def unique_trash_name(path: str) -> str:
    """Get a unique name in the tash directory

    Args:
        path (str): The trash destination path

    Returns:
        str: A unique-named version of path
    """
    suffix = 1
    unique_path = path

    while exists(unique_path):
        base, ext = splitext(path)
        unique_path = base + f"_{suffix}" + ext
        suffix += 1

    return unique_path


@cache
def pref() -> tuple[str, str]:
    """Get the binaries_dir and the trash dir

    Returns:
        tuple[str, str]: binaries_dir from genweb.yml and a calculated trash directory
    """
    settings = load_yaml(join(Settings.PREF_DIR[os_system()], "genweb.yml"))
    cleanup_dir = settings["binaries_dir"]
    trash_dir = join(dirname(dirname(cleanup_dir)), basename(cleanup_dir) + "_trash")
    makedirs(trash_dir, exist_ok=True)
    return (cleanup_dir, trash_dir)


def trash(relative: str):
    """Move the path relative to binaries_dir to the trash dir

    Args:
        relative (str): The relative path inside binaries_dir of file to remove
    """
    cleanup_dir, trash_dir = pref()
    path = join(cleanup_dir, relative)

    if not exists(path):
        return

    destination = unique_trash_name(join(trash_dir, relative))
    makedirs(dirname(destination), exist_ok=True)

    if DRY_RUN:
        print("DRY RUN:")
        print(f"\t MOVE: {path}")
        print(f"\t   TO: {destination}")
        return

    move(path, destination)


def patchup(patchup_list: list[tuple]):
    """Given a list of file extension, regex, replacement, and description, apply them to files.
        If

    Args:
        patchup_list (list[tuple]): List patch ups to perform
    """
    all_files = [join(r, f) for r, _, fs in walk(pref()[0]) for f in fs]

    for path in all_files:
        patches = [p for p in patchup_list if p[0].lower() == splitext(path)[1].lower()]

        if not patches:
            continue

        with open(path, "r", encoding="utf-8") as file:
            contents = file.read()

        modified_contents = contents

        for _, pattern, replacement, reason in patches:
            if not pattern.search(modified_contents):
                continue

            if DRY_RUN:
                print("=" * 80)
                print(path)
                print("=" * 20 + f" before {reason} " + "=" * 20)
                print(modified_contents)

            modified_contents = pattern.sub(replacement, modified_contents)

            if DRY_RUN:
                print("=" * 20 + f" after {reason} " + "=" * 20)
                print(modified_contents)
                return

        if contents == modified_contents:
            continue

        trash(relpath(path, pref()[0]))

        with open(path, "w", encoding="utf-8") as file:
            file.write(modified_contents)


def main() -> None:
    """parses the directories and makes known needed fixes"""
    trash("PedigreeCharts")
    patchup(
        [
            (
                ".xml",
                regex(r'^(\?xml version="1\.0" encoding="ISO-8859-1"\?>)'),
                r"<\1",
                "missing < in header tag",
            ),
            (
                ".xml",
                regex(r"(<title>.*)</caption>"),
                r"\1</title>",
                "<title> paird with </caption>",
            ),
            (
                ".xml",
                regex(r"(([\r\n]+)<inline>.*</people>)$", DOTALL),
                r"\1\2</inline>",
                "missing </inline> at the end",
            ),
            (
                ".xml",
                regex(r"(<title>((?!</title>).)*)([\r\n]+)(.*</title>)"),
                r"\1\4",
                "<title> tag broken into two lines (fix for next pattern)",
            ),
            (
                ".xml",
                regex(r"(<title>((?!</title>).)*)([\r\n]+)"),
                r"\1</title>\3",
                "missing </title>",
            ),
            (
                ".xml",
                regex(r"<!\[CDATA\[(.*?)\]\]>", DOTALL),
                r"\1",
                "Remove CDATA",
            ),
            (
                ".xml",
                regex(r"&(quot|apos|lt|gt|amp);"),
                r"<<<<<\1>>>>>",
                "pre-process expected & elements",
            ),
            (
                ".xml",
                regex(r"&"),
                r"&amp;",
                "escape &",
            ),
            (
                ".xml",
                regex(r"<<<<<(quot|apos|lt|gt|amp)>>>>>"),
                r"&\1;",
                "post-process expected & elements",
            ),
            (
                ".xml",
                regex(r"&amp;"),
                r"&",
                "Convert back &amp;",
            ),
            (
                ".xml",
                regex(r"&quot;"),
                r'"',
                "Convert back &quot;",
            ),
            (
                ".xml",
                regex(r"&apos;"),
                r"'",
                "Convert back &apos;",
            ),
            (
                ".xml",
                regex(r"&lt;"),
                r"<",
                "Convert back &lt;",
            ),
            (
                ".xml",
                regex(r"&gt;"),
                r">",
                "Convert back &gt;",
            ),
            (
                ".xml",
                regex(r"<(caption)>(.+?)</(caption)>", DOTALL),
                r"<\1><![CDATA[\2]]></\3>",
                "CDATA caption",
            ),
            (
                ".xml",
                regex(r"<(title)>(.+?)</(title)>", DOTALL),
                r"<\1><![CDATA[\2]]></\3>",
                "CDATA title",
            ),
            (
                ".xml",
                regex(r"<(comment)>(.+?)</(comment)>", DOTALL),
                r"<\1><![CDATA[\2]]></\3>",
                "CDATA comment",
            ),
            (
                ".xml",
                regex(r"<people>(.*)<people>"),
                r"<people>\1</people>",
                "people end tag missing /",
            ),
            (
                ".xml",
                regex(r"<path>(.*[^<])/path>"),
                r"<path>\1</path>",
                "path end tag missing <",
            ),
            (
                ".xml",
                regex(r'<\?(xml version="1.0")>'),
                r"<?\1?>",
                "xml header missing ending ?",
            ),
        ],
    )


if __name__ == "__main__":
    main()
