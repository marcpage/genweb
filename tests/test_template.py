#!/usr/bin/env python3

""" Test template rendering """

from os.path import join, dirname
from tempfile import TemporaryDirectory

from genweb.template import render, render_to_file


DATA_DIR = join(dirname(__file__), "data")


def test_render_to_file() -> None:
    with TemporaryDirectory() as working_dir:
        output_path = join(working_dir, "results.html")
        render_to_file(
            output_path, join(DATA_DIR, "test.html.mako"), name="Fred", color="Orange"
        )

        with open(output_path, "r", encoding="utf-8") as file:
            contents = file.read()

    assert "Fred" in contents, contents
    assert "Orange" in contents, contents


def test_basic() -> None:
    output = render(join(DATA_DIR, "test.html.mako"), name="Fred", color="Orange")
    assert "Fred" in output, output
    assert "Orange" in output, output


if __name__ == "__main__":
    test_basic()
    test_render_to_file()
