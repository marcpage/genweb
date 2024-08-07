#!/usr/bin/env python3

""" Test template rendering """

from os.path import join, dirname

from genweb.template import render


DATA_DIR = join(dirname(__file__), "data")


def test_basic() -> None:
    output = render(join(DATA_DIR, "test.html.mako"), name="Fred", color="Orange")
    assert "Fred" in output, output
    assert "Orange" in output, output


if __name__ == "__main__":
    test_basic()
