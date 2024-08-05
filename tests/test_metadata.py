#!/usr/bin/env python3

""" Test parsing the yaml """

from genweb.metadata import load
from genweb import metadata

EXAMPLE1 = """
2019090600PageMichaelA2004IngramJamieL1971:
    type: inline
    file: 2019090600BrackenMadisonK2004PageDeborahA1976.src
    title: Maddie and Kaden - 6 September 2019
    people: [BrackenMadisonK2004PageDeborahA1976,BrackenKadenR2002PageDeborahA1976] 
    mod_date: 2020-05-17

2007080001HislopArthurQ1924EuansLauraM1904:
    type: picture
	path: HislopArthurQ1924EuansLauraM1904</path>
	file: 2007080001HislopArthurQ1924EuansLauraM1904.jpg</file>
	caption: Neil Clark, Dorothy, Art, Ann, Bob at the headstone of Arthur W. Hislop and Laura Mae Euans in Cissna Park Village, Pigeon Grove Township, Iroquois County, Illinois, United States - "Quaker Cemetery"</caption>
	people:
        - CecilHaroldE1934LeonardAmyI1910
        - HislopRobertL1940EuansLauraM1904
        - HislopDorothyC1935EuansLauraM1904
        - HislopAnnaM1934EuansLauraM1904
        - HislopArthurQ1924EuansLauraM1904
"""


class FileLike:
    def __init__(self, path: str, mode: str, encoding: str):
        self.path = path
        self.mode = mode
        self.encoding = encoding


def test_load() -> None:
    metadata.OPEN = FileLike
    load(EXAMPLE1)


if __name__ == "__main__":
    test_load()()
