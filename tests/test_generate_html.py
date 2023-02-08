#!/usr/bin/env python3


import os
import tempfile

import genweb.generate_html


def test_gen_alpha_toc():
    people = [
        {
            'long_genwebid': 'long gen web id',
            'Surname': "surname",
            'Given': ['given1', 'given2'],
            'BirthYear': '1947',
            'DeathYear': '2080',
        },
        {
            'long_genwebid': 'long gen web id 2',
            'Surname': "surname 2",
            'Given': ['given2_1', 'given_22'],
            'BirthYear': '',
            'DeathYear': '355',
        },
        {
            'long_genwebid': 'long gen web id 3',
            'Surname': "surname 3",
            'Given': ['given3_1', 'given3_2'],
            'BirthYear': '1978',
            'DeathYear': '',
        },
        {
            'long_genwebid': 'long gen web id 4',
            'Surname': "surname 4",
            'Given': ['given4_1', 'given4_2'],
            'BirthYear': '1990',
            'DeathYear': '1999',
        }
    ]

    with tempfile.TemporaryDirectory() as workspace:
        genweb.generate_html.save_alpha_toc(os.path.join(workspace, 'alpha_toc.html'), people)

        with open(os.path.join(workspace, 'alpha_toc.html'), 'r', encoding='utf-8') as html_file:
            print(html_file.read())


def test_save_personal():
    family_dict = {
        "target": {
            "long_genwebid": "DoeJohn1988",
            "BirthYear": "1988",
            "DeathYear": "",
            "Nickname": "",
            "FullName": "John Doe",
        }
    }
    persons_xml_dict = {
        'artifacts_info': {}
    }
    admin_email = "john.doe@bigbiz.com"

    with tempfile.TemporaryDirectory() as workspace:
        folders_path = workspace
        genweb.generate_html.save_personal(family_dict, persons_xml_dict, admin_email, folders_path)

        with open(os.path.join(folders_path, family_dict["target"]["long_genwebid"], 'index.html'), 'r', encoding='utf-8') as html_file:
            print(html_file.read())


if __name__ == "__main__":
    test_gen_alpha_toc()
    test_save_personal()
