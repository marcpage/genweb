#!/usr/bin/env python3


from devopsdriver.settings import Settings

from relationships import load_gedcom
from people import People


def main() -> None:
    """Generate the website"""
    settings = Settings(__file__)
    gedcom = load_gedcom(settings["gedcom_path"])
    people = People(gedcom)


if __name__ == "__main__":
    main()
