#!/usr/bin/env python3

# pylint: disable=too-many-lines

"""
    Generates all web pages
"""


import os
import glob
import re
import pickle
import sys

from genweb import rmagic
from genweb import generate_html


class BuildWebPages:  # pylint: disable=too-few-public-methods
    """
    This module will build the family history web pages:
        Build table of contents html files
         - _generate_toc_web(families_dict, folders_path)
        Build hourglass html file for each person
         - _generate_all_hourglass_webs(family_dict, folders_path)
        Build the web page for each person's artifacts
         - _generate_person_web(family_dict, persons_xml_dict, folders_path)

                family_dict is taken from the rootsmagic database
                 family_dict =
                   'target: name_table_entry for target
                   'parents':
                     {'mother: name_table_entry for mother,
                      'father: name_table_entry for father}
                   'spouses' : [{name_table_entry for spouse1},...]
                   'children' : [{name_table_entry for child1},...]
                 where each name_table entry will also have key: 'long_genwebid'
                 and the appropriate value.
                 The key for each target is their long_genwebid

                where the keys for an individual are:
                    'OwnerID'
                    'Surname'
                    'Given' (a list of the given names)
                    'Prefix'
                    'Suffix'
                    'Nickname'
                    'IsPrimary'
                    'BirthYear'
                    'DeathYear'
                    'FullName'

        families_dict only contains revised_name_table info for people who have folders
        sample families_dict entry:
        families_dict =
        {'AbdillAliceH1923SmithAgnessF1900':
            {'spouses': [],
             'children': [],
             'target':
                {'BirthYear': '1923',
                 'Nickname': '',
                 'Given': ['Alice', 'H'],
                 'Sex': 'female',
                 'OwnerID': '15390',
                 'IsPrimary': '1',
                 'Suffix': '',
                 'long_genwebid': 'AbdillAliceH1923SmithAgnessF1900',
                 'GenWebID': 'AbdillAliceH1923',
                 'Prefix': '',
                 'DeathYear': '0',
                 'Surname': 'Abdill',
                 'FullName': 'Abdill, Alice H'
                },
             'parents':
                    {'mother': {'BirthYear': '1900', 'Nickname': '',
                     'Given': ['Agness', 'F'], 'Sex': 'female', 'OwnerID': '2596',
                     'IsPrimary': '1', 'Suffix': '', 'long_genwebid': 'SmithAgnessF1900-',
                     'GenWebID': 'SmithAgnessF1900', 'Prefix': '', 'DeathYear': '0',
                     'Surname': 'Smith', 'FullName': 'Smith, Agness F'},

                     'father': {'BirthYear': '1895', 'Nickname': '',
                     'Given': ['Ralph', 'Gilford'], 'Sex': 'male', 'OwnerID': '2595',
                     'IsPrimary': '1', 'Suffix': '',
                     'long_genwebid': 'AbdillRalphG1895WoolworthMaryE1874',
                     'GenWebID': 'AbdillRalphG1895', 'Prefix': '', 'DeathYear': '1960',
                     'Surname': 'Abdill', 'FullName': 'Abdill, Ralph Gilford'}
                    }
            }
        }

        where tgt_name_table_entry = { 'OwnerID': ,
                                        'Surname': surname,
                                        'Given': given,
                                        'Prefix': ,
                                        'Suffix': ,
                                        'Nickname': ,
                                        'IsPrimary': ,
                                        'BirthYear': ,
                                        'DeathYear': }

        where revised_tgt_name_table_entry = { 'OwnerID': ,
                                        'Surname': surname,
                                        'Given': given,
                                        'Prefix': ,
                                        'Suffix': ,
                                        'Nickname': ,
                                        'IsPrimary': ,
                                        'BirthYear': ,
                                        'DeathYear':,
                                        'Sex':,
                                        'long_genwebid':
                                      }

            persons_xml_dict =
                {'person_info':        [persons_id,mothers_id],
                 'artifacts_info':
                    {artifact_id: {'type':'picture','title':'title txt here', ...
                    }
                    {artifact_id: {'type':'picture','title':'title txt here',...
                    }
                     ...
                }
    """

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def __init__(self, rmagic_path, web_folder, admin_email):
        self.admin_email = admin_email
        folders_path = web_folder
        os.chdir(folders_path)
        dictionaries_path = folders_path + "/___dictionaries"

        self._rmagic_path = rmagic_path
        # _tables keys are:['ChildTable',
        #                   'FamilyTable',
        #                   'NameTable',
        #                   'PersonTable',
        #                   'ownerid_name_table',
        #                   'person_id_person_table',
        #                   'family_id_family_table']
        self._tables = rmagic.fetch_rm_tables(self._rmagic_path)
        self._matched_persons = []

        # For each target person in name_table, create a dictionary containing
        # the name_table information for 'target', 'parents', 'children', 'spouses'
        # The key for each target is their long_genwebid
        # families_dict =
        #   'target: name_table_entry for target
        # where the entry for a given person is:
        #       {
        #           'OwnerID': str(name[0]),
        #           'Surname': name[1],
        #           'Given': given,
        #           'Prefix': name[3],
        #           'Suffix': name[4],
        #           'Nickname': name[5],
        #           'IsPrimary': str(name[6]),
        #           'BirthYear': str(name[7]),
        #           'DeathYear': str(name[8]),
        #           'FullName' : FullName
        #       }
        #   'parents': {'mother: name_table_entry for mother,
        #               'father: name_table_entry for father}
        #   'spouses' : [{name_table_entry for spouse1},...]
        #   'children' : [{name_table_entry for child1},...]
        # where each name_table entry will have the addition key: 'long_genwebid'
        # and the appropriate value.

        families_dict = {}
        revised_name_table_entry = {}
        revised_name_table = {}

        if os.path.isfile(rmagic_path):
            rmagic_mod_time = os.stat(rmagic_path).st_mtime
        else:
            print("line 87: no roots magic mod time ", rmagic_path)
            rmagic_mod_time = 0

        file_name = dictionaries_path + "/aaa_revised_name_table.pikl"
        if os.path.isfile(file_name):
            name_table_pkl_mod_time = os.stat(file_name).st_mtime
        else:
            name_table_pkl_mod_time = 0

        if rmagic_mod_time > name_table_pkl_mod_time:
            files = glob.glob(os.path.join(dictionaries_path, "*.pkl"))
            for file in files:
                os.remove(file)
            files = glob.glob(os.path.join(dictionaries_path, "*.dic"))
            for file in files:
                os.remove(file)
            for name_table_entry in self._tables["NameTable"]:
                if name_table_entry["IsPrimary"] == "0":
                    continue

                revised_name_table_entry = self._get_long_genwebid(name_table_entry)

                if revised_name_table_entry == {}:
                    continue

                family_dict = self._get_family(revised_name_table_entry)

                if family_dict["target"]["OwnerID"] == "":
                    print("line 138 - family_dict = ", family_dict)
                    print(
                        "line 139 - revised_name_table_entry = ",
                        revised_name_table_entry,
                    )

                revised_name_table[
                    revised_name_table_entry["long_genwebid"]
                ] = family_dict
            self._save_dictionary(revised_name_table, file_name)

            with open(f"{file_name}.dict", "w", encoding="utf-8") as dict_txt_file:
                dict_txt_file.write(f"line 137 dict_txt_file: {revised_name_table}")

        else:
            revised_name_table = self._load_dictionary(file_name)

        refresh_get_proj_dict_from_xml = True
        generate_table_of_contents = True
        generate_hourglass = True
        generate_web_pages = True

        if refresh_get_proj_dict_from_xml:
            self._get_proj_dict_from_xml(folders_path)  # saves xml in pickle file
        # people_ids comes
        people_ids = glob.glob("*[0-9][0-9][0-9][0-9]*")

        # ----------------------------------------
        # print('____________________________________')
        # print('The following long genwebids are not found in the RootsMagic database:')
        for person in people_ids:
            # print('line164: person in people_ids = ', str(person))
            if person in revised_name_table:
                families_dict[person] = revised_name_table[person]
                # print('line 167 families_dict = ', str(families_dict))
                # print('line 168 revised_name_table(',str(person),') = ',
                #                                           revised_name_table[person])
            else:
                # print("line 170 - person not in the RootsMagic database: person = ",
                #                                                           str(person))
                pass

        # print('End of list')
        # generating toc web pages
        if generate_table_of_contents:
            self._generate_toc_web(families_dict, folders_path)

        # ----------------------------------------

        family_dict = {}
        for long_genwebid in people_ids:  # people_ids = list of folder names
            # load the xml info for this person
            current_file = dictionaries_path + "/" + long_genwebid + ".pkl"
            persons_xml_dict = self._load_dictionary(current_file)

            if long_genwebid in families_dict:
                family_dict = families_dict[long_genwebid]
            else:
                print(
                    "line 235: long_genwebid = ",
                    long_genwebid,
                    "  is not a valid key in families_dict",
                )
                continue
            if generate_web_pages and persons_xml_dict["artifacts_info"] != {}:
                self._generate_person_web(family_dict, persons_xml_dict, folders_path)

            if generate_hourglass:  # this must come after generate_web_pages -
                # don't want hourglass if no web page
                self._generate_all_hourglass_webs(family_dict, folders_path)

    # --------------------------------------------------__init__

    # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements
    def _get_long_genwebid(self, tgt_name_table_entry):
        # Given a person's PersonID (AKA OwnerID) generate the long_genwebid
        # The return is the [long_genwebid, revised_tgt_name_table_entry]
        # self._tables keys are:['ChildTable',
        #                        'FamilyTable',
        #                        'NameTable',
        #                        'PersonTable',
        #                        'ownerid_name_table',
        #                        'person_id_person_table',
        #                        'family_id_family_table']
        family_id_family_table = self._tables["family_id_family_table"]
        person_id_person_table = self._tables["person_id_person_table"]
        ownerid_name_table = self._tables["ownerid_name_table"]

        debug = False
        # print('tgt_name_table_entry = ', str(tgt_name_table_entry))
        if tgt_name_table_entry == {}:
            return {}

        if tgt_name_table_entry["OwnerID"] == "":
            debug = True

        revised_tgt_name_table_entry = tgt_name_table_entry
        if person_id_person_table[tgt_name_table_entry["OwnerID"]]["Sex"] == "0":
            person_sex = "male"
        else:
            person_sex = "female"
        revised_tgt_name_table_entry["Sex"] = person_sex

        if tgt_name_table_entry["BirthYear"] == "0":
            birth_year = "0000"
        elif len(tgt_name_table_entry["BirthYear"]) == 3:
            birth_year = "0" + tgt_name_table_entry["BirthYear"]
        else:
            birth_year = tgt_name_table_entry["BirthYear"]

        revised_tgt_name_table_entry["BirthYear"] = birth_year

        # create the tgt_short_genweb_id
        tgt_short_genweb_id = tgt_name_table_entry["Surname"]

        for given_num in range(len(tgt_name_table_entry["Given"])):
            if (
                given_num == 0 and len(tgt_name_table_entry["Given"][0]) <= 1
            ):  # changed from 2 to 1 20160623
                return {}
            if given_num == 0:
                tgt_short_genweb_id = (
                    tgt_short_genweb_id + tgt_name_table_entry["Given"][0]
                )
                if debug:
                    print("tgt_short_genweb_id1 = ", tgt_short_genweb_id)
            else:
                if debug:
                    print("given_num = ", given_num)
                if len(tgt_name_table_entry["Given"][given_num]) > 0:
                    tgt_short_genweb_id = (
                        tgt_short_genweb_id
                        + tgt_name_table_entry["Given"][given_num][0]
                    )
                if debug:
                    print("tgt_short_genweb_id2 = ", tgt_short_genweb_id)

        tgt_short_genweb_id = tgt_short_genweb_id.replace(".", "")
        tgt_short_genweb_id = tgt_short_genweb_id.replace(" ", "") + birth_year

        # create the mother_short_genweb_id
        # PersonID ==  OwnerID ==  FatherID ==  MotherID ==  SpouseID ==  ChildID
        # ParentID ==  FamilyID

        owner_id = tgt_name_table_entry["OwnerID"]
        # print("tgt_name_table_entry = ", str(tgt_name_table_entry))
        # print('person_id_person_table[', owner_id, '] = ',
        #                                               person_id_person_table[owner_id])
        parent_id = person_id_person_table[owner_id]["ParentID"]

        try:
            family_id_family_table_entry = family_id_family_table[parent_id]
        except:  # pylint: disable=bare-except  # noqa: E722
            long_genwebid = tgt_short_genweb_id + "-"
            revised_tgt_name_table_entry["long_genwebid"] = long_genwebid.replace(
                " ", ""
            )
            return revised_tgt_name_table_entry

        # print("family_id_family_table_entry = ", str(family_id_family_table_entry))
        mother_id = family_id_family_table_entry["MotherID"]

        if mother_id != "0":  # test for mother else set mother_short_genweb_id = '-'
            try:
                mother_name_table_entry = ownerid_name_table[mother_id]
            except:  # pylint: disable=bare-except  # noqa: E722
                # print('mother_id = ', mother_id)
                long_genwebid = tgt_short_genweb_id + "-"
                revised_tgt_name_table_entry["long_genwebid"] = long_genwebid.replace(
                    " ", ""
                )
                return revised_tgt_name_table_entry
        else:
            long_genwebid = tgt_short_genweb_id + "-"
            revised_tgt_name_table_entry["long_genwebid"] = long_genwebid.replace(
                " ", ""
            )
            return revised_tgt_name_table_entry

        if mother_name_table_entry["BirthYear"] == "0":
            birth_year = "0000"
        elif len(mother_name_table_entry["BirthYear"]) == 3:
            birth_year = "0" + mother_name_table_entry["BirthYear"]
        else:
            birth_year = mother_name_table_entry["BirthYear"]

        if len(mother_name_table_entry["Surname"]) > 2:
            mother_short_genweb_id = mother_name_table_entry["Surname"]
        else:
            long_genwebid = tgt_short_genweb_id + "-"
            revised_tgt_name_table_entry["long_genwebid"] = long_genwebid.replace(
                " ", ""
            )
            return revised_tgt_name_table_entry

        for given_num in range(len(mother_name_table_entry["Given"])):
            if given_num == 0 and len(mother_name_table_entry["Given"][0]) <= 2:
                long_genwebid = tgt_short_genweb_id + "-"
                revised_tgt_name_table_entry["long_genwebid"] = long_genwebid.replace(
                    " ", ""
                )
                return revised_tgt_name_table_entry
            if given_num == 0:
                mother_short_genweb_id = (
                    mother_short_genweb_id + mother_name_table_entry["Given"][0]
                )
                if debug:
                    print("mother_short_genweb_id1 = ", mother_short_genweb_id)
            else:
                if debug:
                    print("given_num = ", given_num)
                if len(mother_name_table_entry["Given"][given_num]) > 0:
                    mother_short_genweb_id = (
                        mother_short_genweb_id
                        + mother_name_table_entry["Given"][given_num][0]
                    )
                if debug:
                    print("mother_short_genweb_id2 = ", mother_short_genweb_id)

        mother_short_genweb_id = mother_short_genweb_id.replace(".", "")
        mother_short_genweb_id = mother_short_genweb_id.replace(" ", "") + birth_year

        long_genwebid = tgt_short_genweb_id + mother_short_genweb_id

        # this will be used to identify any problems with long_genwebid
        tgt_person_re = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9]{4}")
        if not tgt_person_re.fullmatch(tgt_short_genweb_id):
            # print('_get_long_genwebid line 304 - problem with tgt_short_genweb_id = ',
            #      tgt_short_genweb_id, '    long_genwebid = ', long_genwebid)
            return {}
        mother_re = re.compile("[-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}")
        if not mother_re.fullmatch(mother_short_genweb_id):
            print(
                "_get_long_genwebid line 308 - problem with mother_short_genweb_id = ",
                mother_short_genweb_id,
                "    long_genwebid = ",
                long_genwebid,
            )
            return {}

        revised_tgt_name_table_entry["long_genwebid"] = long_genwebid
        return revised_tgt_name_table_entry

    # -------------------------------------------------- end of get_long_genwebid

    # pylint: disable=too-many-statements
    def _get_family(self, revised_tgt_name_table_entry):
        """
        where revised_tgt_name_table_entry = { 'OwnerID': ,
                                        'Surname': surname,
                                        'Given': given,
                                        'Prefix': ,
                                        'Suffix': ,
                                        'Nickname': ,
                                        'IsPrimary': ,
                                        'BirthYear': ,
                                        'DeathYear':
                                        'Sex':,
                                        'long_genwebid':
                                      }

        Given a target person's PersonID (OwnerID in name_table)
            1. get the person's Sex from the PersonTable by searching the owner_id
            2. fetch the spouse IDs from the family_table
            3. using the spouse IDs fetch the spouse(s) info from the NameTable

        Given a target person's PersonID (OwnerID in name_table)
            1. get the person's Sex from the PersonTable by searching the owner_id
            2. fetch the FamilyID from the family_table
            3. using the FamilyID fetch the ChildID for each child in the
                ChildTable
            4. Using the ChildID as the OwnerID get each child's info from
                NameTable

         family_dict =
           'target: name_table_entry for target
           'parents': {'mother: name_table_entry for mother,
                        'father: name_table_entry for father}
           'spouses' : [{name_table_entry for spouse1},...]
           'children' : [{name_table_entry for child1},...]
         where each name_table entry will have the addition key: 'long_genwebid'
         and the appropriate value.
         The key for each target is their long_genwebid
        """
        # Given a person's PersonID (AKA OwnerID) generate the long_genwebid
        # The return is the long_genwebid
        # self._tables keys are:['ChildTable',
        #                        'FamilyTable',
        #                        'NameTable',
        #                        'PersonTable',
        #                        'ownerid_name_table',
        #                        'person_id_person_table',
        #                        'family_id_family_table']
        family_id_family_table = self._tables["family_id_family_table"]
        person_id_person_table = self._tables["person_id_person_table"]
        ownerid_name_table = self._tables["ownerid_name_table"]
        child_table = self._tables["ChildTable"]
        name_table = self._tables["NameTable"]
        person_table = self._tables["PersonTable"]
        family_table = self._tables["FamilyTable"]

        # PersonID ==  OwnerID ==  FatherID ==  MotherID ==  SpouseID ==  ChildID
        # ParentID ==  FamilyID

        # MOTHER
        owner_id = revised_tgt_name_table_entry["OwnerID"]
        parent_id = person_id_person_table[owner_id]["ParentID"]
        revised_mother_name_table_entry = {}
        try:
            family_id_family_table_entry = family_id_family_table[parent_id]
            mother_id = family_id_family_table_entry["MotherID"]
            mother_name_table_entry = ownerid_name_table[mother_id]
            revised_mother_name_table_entry = self._get_long_genwebid(
                mother_name_table_entry
            )
        except:  # pylint: disable=bare-except  # noqa: E722
            revised_mother_name_table_entry = {}

        # FATHER
        revised_father_name_table_entry = {}
        try:
            father_id = family_id_family_table_entry["FatherID"]
            father_name_table_entry = ownerid_name_table[father_id]
            revised_father_name_table_entry = self._get_long_genwebid(
                father_name_table_entry
            )
        except:  # pylint: disable=bare-except  # noqa: E722
            revised_father_name_table_entry = {}

        # SPOUSES
        spouses = rmagic.fetch_spouses_from_id(
            name_table, person_table, family_table, owner_id
        )

        # print('spouses = ', str(spouses))
        revised_spouses = []

        if spouses:
            for spouse in spouses:
                if not spouse:
                    continue

                revised_spouse = self._get_long_genwebid(spouse)

                if revised_spouse == {}:
                    continue

                revised_spouses.append(revised_spouse)
                # print('revised_spouse = ', revised_spouse)

        # CHILDREN
        children = rmagic.fetch_children_from_id(
            child_table, name_table, person_table, family_table, owner_id
        )

        # print('children = ', str(children))
        revised_children = []
        if len(children) > 0:
            for child in children:
                revised_child = self._get_long_genwebid(child)
                if revised_child == {}:
                    continue
                revised_children.append(revised_child)
                # print('revised_child = ', str(revised_child))

        family_dict = {}
        family_dict["target"] = revised_tgt_name_table_entry
        family_dict["parents"] = {
            "father": revised_father_name_table_entry,
            "mother": revised_mother_name_table_entry,
        }
        family_dict["spouses"] = revised_spouses
        family_dict["children"] = revised_children
        # print('family_dict = ', family_dict)
        return family_dict

    # -------------------------------------------------- end of _get_family

    # pylint: disable=too-many-branches
    def _get_mothers_child(self, target_genwebid, targets_mother, folders_path):
        """
        Given the persons short genwebid (person, e.g. PageRobertK1953) and
        the person's mother's short genwebid (persons_mother, e.g., HughsM1925),
        returns the person_facts for for that mother/child pair.
        (This differentiates two people with the same name and birth year.)
        match person facts =
        {'GenWebID': 'AbdillAliceH1923', 'Nickname': '', 'BirthYear': '1923',
         'IsPrimary': '1', 'Given': ['Alice', 'H'], 'Surname': 'Abdill',
         'Sex': 'female', 'Prefix': '', 'FullName': 'Abdill, Alice H',
         'DeathYear': '0', 'Suffix': '', 'OwnerID': '15390'}

        Given a person's 'Surname', 'Given', 'Initial', 'BirthYear' fetch the
        NameTable entry for that person. If there is more than one match, they will all
        be returned in a list
        The return is of the form:
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1953','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1953',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
           where these rootsmagic tags are equivalent ; OwnerID = person_ID
        """
        debug = False
        if target_genwebid == "CoxSusan1785":
            debug = True
        proper_format = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]")
        chg_to_long_id_file = open(
            os.path.join(folders_path, "zzz_xml_file_name_issue.txt"),
            "a",
            encoding="utf-8",
        )

        if not proper_format.match(target_genwebid):
            with open(
                os.path.join(folders_path, "zzz_xml_file_name_issue.txt"),
                "a",
                encoding="utf-8",
            ) as chg_to_long_id_file:
                chg_to_long_id_file.write(
                    "_get_mothers_child line 84- improper format for target genwebid "
                    + target_genwebid
                    + "\n"
                )
            return ""

        if target_genwebid == "CoxSusan1785":
            debug = True

        person_id_dict = self._separate_names(target_genwebid)
        person_matches = rmagic.fetch_person_from_name(
            self._tables["NameTable"], self._tables["PersonTable"], person_id_dict
        )
        if debug:
            print(
                "\n _get_mothers_child line 105 - person_matches = ",
                person_matches,
                "\n\t  for person_id_dict = ",
                person_id_dict,
            )
        null_person = rmagic.empty_person(is_primary="")

        if len(person_matches) == 0:
            with open(
                os.path.join(folders_path, "zzz_xml_file_name_issue.txt"),
                "a",
                encoding="utf-8",
            ) as chg_to_long_id_file:
                chg_to_long_id_file.write(
                    "_get_mothers_child line 123- Could not find"
                    + " rmagic match for person with target_genwebid = "
                    + target_genwebid
                    + "\n",
                )
            return null_person

        if len(person_matches) >= 1:
            for match_person in person_matches:
                if debug:
                    chg_to_long_id_file = open(
                        os.path.join(folders_path, "zzz_xml_file_name_issue.txt"),
                        "a",
                        encoding="utf-8",
                    )
                    chg_to_long_id_file.write(
                        "line 129 _get_mothers_child"
                        + " - Multiple matches for rmagic person. Match = "
                        + match_person["GenWebID"]
                        + "\n"
                    )
                parents = rmagic.fetch_parents_from_id(
                    self._tables["PersonTable"],
                    self._tables["NameTable"],
                    self._tables["FamilyTable"],
                    match_person["OwnerID"],
                )
                if debug:
                    print("\n line 135 _get_mothers_child - parents = ", parents)
                mother_id_dict = self._separate_names(parents["Mother"]["GenWebID"])
                if (
                    len(mother_id_dict["Given"]) == 0
                    or len(mother_id_dict["Surname"]) == 0
                ):
                    mothers_genwebid = ""
                else:
                    mothers_genwebid = parents["Mother"]["GenWebID"]
                if mothers_genwebid == targets_mother:
                    chg_to_long_id_file.close()
                    return match_person

        chg_to_long_id_file.write(
            "_get_mothers_child line 173 - Multiple matches not resolved - \n"
            + "\ttarget_genwebid = "
            + target_genwebid
        )
        chg_to_long_id_file.write("\n\ttargets_mother = " + targets_mother + "\n")
        chg_to_long_id_file.write("\n\tmothers_genwebid = " + mothers_genwebid + "\n")
        chg_to_long_id_file.close()
        return null_person

    # --------------------------------------------------_get_mothers_child

    # pylint: disable=too-many-branches,too-many-statements
    def _get_3g_family(self, targets_long_genwebid, folders_path):
        """
        Given the persons long_genwebid (person, e.g.
        PageRobertK1953HughsMarillynM1921) this returns the 3 generation family
        (person, parents, spouses, and children
        3g_family =
        'tgt_person_facts' =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1953','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1953',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        'tgt_parents' = {
            'Father': {'Given': [''], \
                        'IsPrimary': '1', 'DeathYear': '', 'Prefix': '', \
                        'BirthYear': '', 'Nickname': '', 'Suffix': '', 'Surname': '', \
                        'OwnerID': '', 'Sex': '', 'GenWebID': '', 'FullName': ''},\

            'Mother':{'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                        'Prefix': '', 'BirthYear': '', 'Nickname': '', 'Suffix': '', \
                        'Surname': '', 'OwnerID': '', 'Sex': '', 'GenWebID': '', \
                        'FullName': ''}}
        'spouse_list' =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1953','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1953',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        'child_list' =
              [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
                'Suffix': '', 'BirthYear': '1953','Prefix': '',
                'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1953',
                'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
                'FullName': 'Page, Robert Kenneth'}]

        tgt_person_facts =
        [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
            'Suffix': '', 'BirthYear': '1953','Prefix': '',
            'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1953',
            'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
            'FullName': 'Page, Robert Kenneth'}...]

        Given a person's PersonID (AKA OwnerID) fetch the spouse's NameTable
        entries for that person.
        The fetch_person_from_ID return is of the form spouse =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1953','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1953',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        three_gen_family['spouse_list'] is a list of spouse NameTable entries

        Given a person's PersonID (AKA OwnerID) fetch the children's NameTable
        entries for that person.
        The fetch_person_from_ID return is of the form child =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1953','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1953',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        three_gen_family['child_list'] is a list of children NameTable entries
        """
        debug = False
        if targets_long_genwebid == "":
            debug = True
        three_gen_family = {}
        # this will be used to separate the genwebid (target_person)
        # into the persons_id and the mothers_id
        people_re = re.compile(
            "(([A-Za-z']+[A-Z][a-z]*[0-9]{4})' \
                                       + '([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))"
        )

        # this will be used to separate the target person's
        # id from the mother's id
        # tgt_person_stuff of the form: ['PersondateMotherdate','Persondate','Motherdate']
        try:
            tgt_person_stuff = people_re.findall(targets_long_genwebid)  # [0]
        except:  # pylint: disable=bare-except  # noqa: E722
            print(
                "\n _get_3g_family - line 695 targets_long_genwebid = ",
                targets_long_genwebid,
            )
            print(
                " couldn't set tgt_person_stuff = people_re.findall(targets_long_genwebid)[0]"
            )
            three_gen_family["tgt_parents"] = {
                "Father": rmagic.empty_person(),
                "Mother": rmagic.empty_person(),
            }
            return three_gen_family

        tgt_person_stuff = people_re.findall(targets_long_genwebid)[0]

        tgt_person = tgt_person_stuff[1]
        tgt_persons_mother = tgt_person_stuff[2]
        if tgt_persons_mother == "-":
            name_dict = self._separate_names(tgt_person)
            try:
                tgt_person_facts = three_gen_family[
                    "tgt_person_facts"
                ] = rmagic.fetch_person_from_name(
                    self._tables["NameTable"], self._tables["PersonTable"], name_dict
                )[
                    0
                ]
            except:  # pylint: disable=bare-except  # noqa: E722
                tgt_person_facts = three_gen_family[
                    "tgt_person_facts"
                ] = rmagic.fetch_person_from_name(
                    self._tables["NameTable"], self._tables["PersonTable"], name_dict
                )

                print(
                    "\n _get_3g_family - line 179 tgt_person_facts = ",
                    tgt_person_facts,
                    "\n name_dict = ",
                    name_dict,
                )
        else:
            tgt_person_facts = self._get_mothers_child(
                tgt_person, tgt_persons_mother, folders_path
            )

            three_gen_family["tgt_person_facts"] = tgt_person_facts

        if debug:
            print(
                "\n _get_3g_family - line 186 \
                three_gen_family[tgt_person_facts] = ",
                three_gen_family["tgt_person_facts"],
            )
        # add target person's parents
        # Build targets father - possibilities are that:
        #                    - there is no father's name in the person's entry
        #                                   - father's position empty and no link
        #                    - there is a father's name in the person's entry
        #                                   - father's position (if no record,
        #                                                              no name available)
        #                    - there is a record for the father
        #                                   - father's position and link
        #                    - there is not a record for the father
        #                                   - no father's position and no link
        # Calls to rmagic.fetch_parents return:
        #
        #        father = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
        #                   'Prefix': '', 'BirthYear': '', 'Nickname': '', \
        #                   'Suffix': '', 'Surname': '', 'OwnerID': '',
        #                   'Sex': '', 'GenWebID': '', 'FullName': ''}
        #
        #       mother = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
        #                   'Prefix': '', 'BirthYear': '', 'Nickname': '', \
        #                   'Suffix': '', 'Surname': '', 'OwnerID': '',
        #                   'Sex': '', 'GenWebID': '', 'FullName': ''}
        #  where return = {'Father': father, 'Mother': mother}
        try:
            three_gen_family["tgt_parents"] = rmagic.fetch_parents_from_id(
                self._tables["PersonTable"],
                self._tables["NameTable"],
                self._tables["FamilyTable"],
                three_gen_family["tgt_person_facts"]["OwnerID"],
            )
        except:  # pylint: disable=bare-except  # noqa: E722  # noqa: E722
            print(
                "\n _get_3g_family - line 222 \
                three_gen_family[tgt_person_facts] = ",
                str(three_gen_family["tgt_person_facts"]),
                "\n targets_long_genwebid = ",
                targets_long_genwebid,
            )

            three_gen_family["tgt_parents"] = {
                "Father": rmagic.empty_person(),
                "Mother": rmagic.empty_person(),
            }

        if debug:
            print(
                "\n _get_3g_family - line 225 tgt_parents = ",
                str(three_gen_family["tgt_parents"]),
            )

        tgt_fathers_owner_id = three_gen_family["tgt_parents"]["Father"]["OwnerID"]
        if tgt_fathers_owner_id != "":
            three_gen_family["tgt_fathers_parents"] = rmagic.fetch_parents_from_id(
                self._tables["PersonTable"],
                self._tables["NameTable"],
                self._tables["FamilyTable"],
                tgt_fathers_owner_id,
            )
            if debug:
                print(
                    "\n _get_3g_family - line 234 tgt_fathers_parents = ",
                    str(three_gen_family["tgt_fathers_parents"]),
                )

        tgt_mothers_owner_id = three_gen_family["tgt_parents"]["Mother"]["OwnerID"]
        if tgt_mothers_owner_id != "":
            three_gen_family["tgt_mothers_parents"] = rmagic.fetch_parents_from_id(
                self._tables["PersonTable"],
                self._tables["NameTable"],
                self._tables["FamilyTable"],
                tgt_mothers_owner_id,
            )

            if debug:
                print(
                    "\n _get_3g_family - line 243 tgt_mothers_parents = ",
                    str(three_gen_family["tgt_mothers_parents"]),
                )

        # I now have the target person's spouse's info
        three_gen_family["spouse_list"] = rmagic.fetch_spouses_from_id(
            self._tables["NameTable"],
            self._tables["PersonTable"],
            self._tables["FamilyTable"],
            three_gen_family["tgt_person_facts"]["OwnerID"],
        )

        if debug:
            print(
                "\n _get_3g_family - line 262 spouselist = ",
                str(three_gen_family["spouse_list"]),
            )

        # add children
        three_gen_family["child_list"] = rmagic.fetch_children_from_id(
            self._tables["ChildTable"],
            self._tables["NameTable"],
            self._tables["PersonTable"],
            self._tables["FamilyTable"],
            three_gen_family["tgt_person_facts"]["OwnerID"],
        )

        if debug:
            print(
                "\n _get_3g_family - line 240 child_list = ",
                str(three_gen_family["child_list"]),
            )

        return three_gen_family

    # --------------------------------------------------_get_3g_family

    def _save_dictionary(self, dictionary, file_name):
        with open(file_name, "wb") as my_file:
            pickle.dump(dictionary, my_file)

    def _load_dictionary(self, file_name):
        if not os.path.isfile(file_name):
            print("_load_dictionary with file_name= ", file_name, "  not found")
            return {"person_info": [], "artifacts_info": {}}

        with open(file_name, "rb") as my_file:
            dictionary = pickle.load(my_file)
            return dictionary

    # -------------------------------------------------- pickle load and save

    # pylint: disable=too-many-branches,too-many-statements
    def _get_proj_dict_from_xml(self, folders_path):
        """
        Build a dictionary with each person's genwebid as a key. Each person's
        key will be attached to a dictionary containing zero or more artifacts.
        Each artifact will consist of a key (the artifact_id) of the
        form:
        YYYYMMDD##Last_nameFirst_nameMiddle_initialYYYYLast_nameFirst_nameMiddle_initialYYYY
        where the first date in the id is the date of the artifact (birth, death,
        marriage, etc.) followed by the genwebid of the person whose
        folder has "custody" of the artifact which is followed by the genwebid
        of the persons mother. Associated with that artifact key
        is a dictionary of the artifact description. The artifact description
        has a key indicating the type of artifact ('inline','picture','href')
        and the data elements describing the artifact and it's location: 'path',
        'file','folder','title','caption','comment','people','height','mod_dat'
        """
        os.chdir(folders_path)
        dictionaries_path = folders_path + "/___dictionaries"
        if not os.path.isdir(dictionaries_path):
            os.makedirs(dictionaries_path)
        # I only want folders that have at least a first and last name with a
        # four digit number for the target person and followed by either a "-"
        # or a first and last name with a four digit number for the mother
        folders = glob.glob("*[0-9][0-9][0-9][0-9]*")

        # this will be used to separate the long_genwebid
        # into the persons_id and the mothers_id
        people_re = re.compile(
            "(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))"
        )

        # this will be used to ensure that the artifact xml filename has the proper form
        proper_format = re.compile(
            "[+]*[0-9]{10}[A-Za-z']+[A-Z][a-z]*[0-9]{4}([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4})"
        )
        debug = False
        person_dict = {}

        for folder in folders:  # step through each folder
            long_genwebid = folder.strip()
            if folder != long_genwebid:
                print(
                    "_get_proj_dict_from_xml folder: ",
                    folder,
                    "  has some spaces in its name",
                )
                continue
            if folder == "":
                debug = True

            if folder == "20181114.ged":
                continue

            if long_genwebid == "":
                continue
            if debug:
                print(
                    "*** _get_proj_dict_from_xml line 355 - \
                    current folder = ",
                    folder,
                    "\n\t people_re.findall(folder) = ",
                    people_re.findall(folder),
                )
            try:
                # if there is an error in the following line it is probably
                # caused my either and incomplete xml reference or an incorrect
                # folder name (not a long genwebid)
                # person_stuff of the form:
                #               ['PersondateMotherdate','Persondate','Motherdate']
                person_stuff = people_re.findall(folder)[0]
            except:  # pylint: disable=bare-except  # noqa: E722
                print(
                    "*** _get_proj_dict_from_xml line 937 folder either and incomplete "
                    + "xml reference or an incorrect folder name "
                    + "(not a long genwebid) folder = ",
                    folder,
                )
                continue
            if len(person_stuff) == 0 or len(person_stuff[0]) < 3:
                print(
                    "\n _get_proj_dict_from_xml line 179 long_genwebid = ",
                    long_genwebid,
                    "   person_stuff = ",
                    person_stuff,
                )
                # dictionary entry will be of the form:
                #                   'AbdillAliceH1923SmithAgnessF1900':{}
                continue

            # persons_id = person_stuff[0][1] and mothers_id = person_stuff[0][2]
            # Create dictionary entry for long_genwebid
            person_dict = {
                "person_info": [person_stuff[1], person_stuff[2]],
                "artifacts_info": {},
            }

            os.chdir(folders_path + "/" + folder)
            # xml files are artifact description files
            xml_file_names = glob.glob("*.xml")
            # if there are no xml files in this person's folder
            if len(xml_file_names) == 0:
                current_file = dictionaries_path + "/" + long_genwebid + ".pkl"
                self._save_dictionary(person_dict, current_file)
                current_file = dictionaries_path + "/" + long_genwebid + ".dic"

                with open(current_file, "w", encoding="utf-8") as dictionary_file:
                    dictionary_file.write(str(person_dict))

                continue  # move on to the next folder

            artifacts_dictionary = {}
            for xml_file_name in xml_file_names:  # step through the xml files
                if xml_file_name == "":
                    debug = True

                # if  xml file name doesn't match the folder name
                if long_genwebid not in xml_file_name:
                    with open(
                        os.path.join(folders_path, "zzz_xml_file_name_issue.txt"),
                        "a",
                        encoding="utf-8",
                    ) as xml_file_name_issue_file:
                        xml_file_name_issue_file.write(
                            "*****\
                                _get_proj_dict_from_xml file name line 192 "
                            + xml_file_name
                            + " should Not be in "
                            + folder
                            + "\n"
                        )
                    continue

                xml_id = xml_file_name.rstrip(".xml")
                if not proper_format.match(xml_id):
                    with open(
                        os.path.join(folders_path, "zzz_xml_file_name_issue.txt"),
                        "a",
                        encoding="utf-8",
                    ) as xml_file_name_issue_file:
                        xml_file_name_issue_file.write(
                            "*****\
                            _get_proj_dict_from_xml file name line 199  "
                            + folder
                            + "/"
                            + xml_file_name
                            + " does not have the proper data format\n"
                        )
                    continue

                # create a dictionary of xml file contents
                with open(xml_file_name, "r", encoding="utf-8") as current_xml_file:
                    # print("xml file name = ", xml_file_name)
                    artifact_dictionary = {}

                    # used to create the dictionary of xml file contents
                    tags = [
                        "<path>",
                        "<file>",
                        "<folder>",
                        "<title>",
                        "<caption>",
                        "<comment>",
                        "<people>",
                        "<height>",
                        "<mod_date>",
                    ]
                    types = ["<inline>", "<picture>", "<href>"]
                    tags_types = tags + types
                    # extract all data from the current xml file
                    # pylint: disable=too-many-nested-blocks
                    for line in current_xml_file:
                        line = line.lstrip(" ")
                        line = line.replace("<![CDATA[", "")
                        line = line.replace("]]>", "")
                        line = line.replace("\n", "")
                        line = line.replace("\t", "")
                        lc_line = line.lower()
                        for tag_type in list(tags_types):
                            if tag_type in lc_line:
                                if tag_type == "":
                                    debug = True

                                # I found it here, I don't want to look for it
                                # again in this xml file
                                tags_types.remove(tag_type)
                                if debug:
                                    print(
                                        "\n _get_proj_dict_from_xml line 232 \
                                        tags_types = ",
                                        tags_types,
                                    )
                                if tag_type in types:
                                    artifact_dictionary["tag_type"] = tag_type.strip(
                                        "<>/"
                                    )
                                    break

                                if tag_type in tags:
                                    line = line.replace(tag_type, "")
                                    line = line.replace("</" + tag_type[1:], "")
                                    if tag_type == "<people>":
                                        people_list = []
                                        people_in_artifact = line.split(";")

                                        # person_in_artifact is a long genwebid
                                        for person_in_artifact in people_in_artifact:
                                            person_in_artifact_stripped = (
                                                person_in_artifact.strip()
                                            )
                                            if person_in_artifact_stripped == "":
                                                continue
                                            # if person_in_artifact_stripped == long_genwebid: continue
                                            # person's artifact is already in their own dictionary entry
                                            if debug:
                                                print(
                                                    "\n line 426: person_in_artifact_stripped = ",
                                                    person_in_artifact_stripped,
                                                )
                                            # if person doesn't have a folder(i.e. not already in the dictionary
                                            if (
                                                person_in_artifact_stripped
                                                not in folders
                                            ):
                                                print(
                                                    "\n _get_proj_dict_from_xml line 430 person_in_artifact_stripped = ",
                                                    person_in_artifact_stripped,
                                                    " folder not found",
                                                )
                                                with open(
                                                    folders_path
                                                    + "/zzz_People with no folder.txt",
                                                    "a",
                                                    encoding="utf-8",
                                                ) as person_no_folder:
                                                    person_no_folder.write(
                                                        "person_in_artifact with no folder = "
                                                        + person_in_artifact_stripped
                                                        + "\n"
                                                    )
                                                    person_no_folder.write(
                                                        "check the people field of artifact: "
                                                        + xml_file_name
                                                        + "\n"
                                                    )
                                                    person_no_folder.write(
                                                        "long_genwebid = "
                                                        + long_genwebid
                                                        + "\n"
                                                    )

                                                os.makedirs(
                                                    os.path.join(
                                                        folders_path,
                                                        person_in_artifact_stripped,
                                                    )
                                                )
                                                # Create entry
                                                try:
                                                    person_stuff = people_re.findall(
                                                        person_in_artifact_stripped
                                                    )[
                                                        0
                                                    ]  # of the form: ['PersondateMotherdate', 'Persondate', 'Motherdate']
                                                    overall_dictionary[
                                                        person_in_artifact_stripped
                                                    ] = {
                                                        "person_info": [
                                                            person_stuff[1],
                                                            person_stuff[2],
                                                        ]
                                                    }
                                                except:  # pylint: disable=bare-except  # noqa: E722
                                                    print(
                                                        "\n _get_proj_dict_from_xml line 441 person_in_artifact_stripped = ",
                                                        person_in_artifact_stripped,
                                                    )
                                                    print(
                                                        "\n _get_proj_dict_from_xml line 442 artifact_dictionary = ",
                                                        artifact_dictionary,
                                                    )
                                                continue
                                            people_list.append(
                                                person_in_artifact_stripped
                                            )

                                        artifact_dictionary[
                                            tag_type.strip("<>/")
                                        ] = people_list  # final list of people
                                        break

                                    artifact_dictionary[tag_type.strip("<>/")] = line
                                    break
                    if debug:
                        print(
                            "\n _get_proj_dict_from_xml line 270 \
                                   artifact_dictionary = ",
                            artifact_dictionary,
                        )
                    artifacts_dictionary[xml_id] = artifact_dictionary
            person_dict["artifacts_info"] = artifacts_dictionary

            if debug:
                print(
                    "_get_proj_dict_from_xml line 291 \
                      long_genwebid = ",
                    long_genwebid,
                    "\n   \
                       person_dict = ",
                    person_dict,
                )
            current_file = dictionaries_path + "/" + long_genwebid + ".pkl"
            self._save_dictionary(person_dict, current_file)
            current_file = dictionaries_path + "/" + long_genwebid + ".dic"
            with open(current_file, "w", encoding="utf-8") as dictionary_file:
                dictionary_file.write(str(person_dict))

        # assign all artifacts to all of the appropriate people

        os.chdir(folders_path)
        folders = glob.glob("*[0-9][0-9][0-9][0-9]*")

        debug = False

        # step through each persons dictionary entry and copy their artifacts into
        # the dictionary for each person appearing in that artifact

        for folder in folders:  # step through each folder's dictionary
            long_genwebid = folder.strip()

            current_file = dictionaries_path + "/" + long_genwebid + ".pkl"
            if os.path.exists(current_file):
                person_dict = self._load_dictionary(current_file)
            else:
                continue

            # no artifact files for this person
            if person_dict["artifacts_info"] == {}:
                continue

            if debug:
                print("\n line 306: long_genwebid = ", long_genwebid, "\n")
            if debug:
                print("\n line 307: person_dict = ", person_dict, "\n")
            genwebid_artifacts_dict = person_dict["artifacts_info"]
            if debug:
                print(
                    "\n line 309: genwebid_artifacts_dict = ",
                    genwebid_artifacts_dict,
                    "\n",
                )
            genwebid_person_info_dict = person_dict["person_info"]
            if debug:
                print(
                    "\n line 311: genwebid_person_info_dict = ",
                    genwebid_person_info_dict,
                    "\n",
                )
            genwebid_artifacts_dict_keys = sorted(genwebid_artifacts_dict.keys())
            if debug:
                print(
                    "\n line 313: genwebid_artifacts_dict_keys = ",
                    genwebid_artifacts_dict_keys,
                    "\n",
                )

            for genwebid_artifact_dict_id in genwebid_artifacts_dict:
                debug = genwebid_artifact_dict_id == ""

                if debug:
                    print(
                        "\n \n _get_proj_dict_from_xml line 1131 \
                        genwebid_artifact_dict_id = ",
                        genwebid_artifact_dict_id,
                    )

                try:
                    genwebid_artifact_dict_people = genwebid_artifacts_dict[
                        genwebid_artifact_dict_id
                    ]["people"]
                except:  # pylint: disable=bare-except  # noqa: E722
                    print(
                        "line 1166: genwebid_artifacts_dict[genwebid_artifact_dict_id][people] Probable KeyError: people"
                    )
                    print(
                        "line 1166: genwebid_artifact_dict_id = ",
                        genwebid_artifact_dict_id,
                    )
                    continue
                if debug:
                    print(
                        "\n  _get_proj_dict_from_xml line 322 \
                        genwebid_artifact_dict_people = ",
                        genwebid_artifacts_dict[genwebid_artifact_dict_id]["people"],
                    )

                for person_in_artifact in genwebid_artifact_dict_people:
                    # if the person has no artifacts assigned
                    if person_in_artifact == "-":
                        with open(
                            os.path.join(folders_path, "zzz_PeopleNotFound.txt"),
                            "a",
                            encoding="utf-8",
                        ) as not_found_file:
                            not_found_file.write(
                                "++++++++++++++++ "
                                + "_get_proj_dict_from_xml line 318 ++++++++++++\n"
                            )
                            not_found_file.write(
                                "person_in_artifact = "
                                + person_in_artifact
                                + "\n genwedid_artifact_dict = "
                                + genwedid_artifact_dict
                                + "\n"
                            )
                            not_found_file.write(
                                "check the people field of "
                                + genwedid_artifact_dict
                                + "\n"
                            )
                            not_found_file.write(
                                "long_genwebid = "
                                + long_genwebid
                                + "\n genwedid_artifact_dict = "
                                + genwedid_artifact_dict
                                + "\n"
                            )
                    else:
                        current_file = (
                            dictionaries_path + "/" + person_in_artifact + ".pkl"
                        )
                        if os.path.exists(current_file):
                            artifact_person_dict = self._load_dictionary(current_file)
                        # add artifact
                        artifact_person_dict["artifacts_info"][
                            genwebid_artifact_dict_id
                        ] = person_dict["artifacts_info"][genwebid_artifact_dict_id]
                        current_file = (
                            dictionaries_path + "/" + person_in_artifact + ".pkl"
                        )
                        self._save_dictionary(artifact_person_dict, current_file)
                        current_file = (
                            dictionaries_path + "/" + person_in_artifact + ".dic"
                        )
                        with open(
                            current_file, "w", encoding="utf-8"
                        ) as dictionary_file:
                            dictionary_file.write(str(artifact_person_dict))

                    debug = False

    # --------------------------------------------------_get_proj_dict_from_xml

    # pylint: disable=too-many-branches
    def _separate_names(self, item):
        """given a string that is a concatenation of names with their first
        letters capitalized [e.g. PageRobertK1953], separate them into
        separate words or characters and the date -
        assumes person IDs contain no spaces and every person's ID has
        a date or 0000
        The results are a dictionary with the following keys
        'BirthYear'
        'Surname'
        'Given'
        'Initial'
        'FullName = person['Surname'] + ', ' + person['Given'] + ' ' + person['Initial']'
        """
        if item == "":
            person = {
                "BirthYear": "",
                "Surname": "",
                "Given": "",
                "Initial": "",
                "FullName": "",
            }
            return person
        # extract the date
        debug = False
        if item == "":
            debug = True
        person = {}
        person["BirthYear"] = item.strip(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'"
        )
        item = item.strip("0123456789")

        people_re = re.compile(r"([A-Z][a-z]+)")

        names = people_re.split(item)
        names = [x for x in names if x != ""]

        if len(names) < 2 and debug:
            print(
                "\n line 402 _separate_names: item = ",
                item,
                "\n  names = ",
                names,
                "\n",
            )
            person = {
                "BirthYear": "",
                "Surname": "",
                "Given": "",
                "Initial": "",
                "FullName": "",
            }
            return person

        surname_exceptions = [
            "O'",
            "ap",
            "de",
            "De",
            "le",
            "Le",
            "Mc",
            "Mac",
            "Van",
            "of",
            "St",
        ]
        givenname_exceptions = ["De"]

        person["Surname"] = ""
        person["Given"] = ""
        person["Initial"] = ""

        if names[0] in surname_exceptions:
            person["Surname"] = names[0] + names[1]
            if names[2] in givenname_exceptions:
                person["Given"] = names[2] + names[3]
                if len(names) == 5:
                    person["Initial"] = names[4]
            else:
                person["Given"] = names[2]
                if len(names) == 4:
                    person["Initial"] = names[3]

        else:
            person["Surname"] = names[0]
            if names[1] in givenname_exceptions:
                person["Given"] = names[1] + names[2]
                if len(names) == 4:
                    person["Initial"] = names[3]
            else:
                person["Given"] = names[1]
                if len(names) == 3:
                    person["Initial"] = names[2]

        person["FullName"] = (
            person["Surname"] + ", " + person["Given"] + " " + person["Initial"]
        )

        if item != person["Surname"] + person["Given"] + person["Initial"]:
            print(
                "item = ",
                item,
                " person full name = ",
                person["Given"],
                " ",
                person["Initial"],
                " ",
                person["Surname"],
            )
        return person

    # -------------------------------------------------- _separate_names

    @staticmethod
    def _first_letter(people_info, long_genwebid):
        name = people_info[long_genwebid]["target"]["Surname"]
        return "de" if name.startswith("de") else name[0]

    def _generate_alpha_toc_info(self, people_info):
        first_letters = {
            BuildWebPages._first_letter(people_info, k) for k in people_info
        }
        return {
            fl: [
                people_info[k]["target"]
                for k in people_info
                if BuildWebPages._first_letter(people_info, k) == fl
            ]
            for fl in first_letters
        }

    def _generate_toc_web(self, people_info, folders_path):
        """
        This generates the Table of Contents web pages for the whole website.
        people_info for PageRobertK1953HughsMarillynM1925 =
        {'parents':
        {
        'father': {'long_genwebid': 'PageRaymondH1921StadtfeldLucyS1895', ...},

        'mother': {'long_genwebid': 'HughsMarillynM1925CorbettVerneI1892', ...}
        },

        'children':
        [{'Sex': 'male', 'FullName': 'Page, Marc Allen', 'IsPrimary': '1', ...},
         ...],

        'target':
        {
        'long_genwebid': 'PageRobertK1953HughsMarillynM1925', ...]
        },

        'spouses':
        [{'Sex': 'female', 'FullName': 'Hislop, Mickie Louise', ...}]
        }

        where the keys for an individual are:
            'OwnerID'
            'Surname'
            'Given' (a list of the given names)
            'Prefix'
            'Suffix'
            'Nickname'
            'IsPrimary'
            'BirthYear'
            'DeathYear'
            'long_genwebid'
        """
        people_by_alpha = self._generate_alpha_toc_info(people_info)

        for first_letter, people_with_first_letter in sorted(people_by_alpha.items()):
            alpha_index_path = os.path.join(folders_path, f"{first_letter}.html")
            generate_html.save_alpha_toc(alpha_index_path, people_with_first_letter)

        return  # return from _generate_toc_web

    # -------------------------------------------------- end of _generate_toc_web

    def _last(self, item):  # used in _generate_person_web
        return item[-4:]

    # --------------------------------------------------

    def _generate_person_web(self, family_dict, persons_xml_dict, folders_path):
        generate_html.save_personal(
            family_dict, persons_xml_dict, self.admin_email, folders_path
        )

    # -------------------------------------------------- end of _generate_person_web

    # pylint: disable=too-many-branches,too-many-statements
    def _generate_all_hourglass_webs(self, family_dict, folders_path):
        """
        This is the new one! changing from person to family_dict

         family_dict =
           'target: name_table_entry for target
           'parents':
             {'mother: name_table_entry for mother,
              'father: name_table_entry for father}
           'spouses' : [{name_table_entry for spouse1},...]
           'children' : [{name_table_entry for child1},...]
         where each name_table entry will also have key: 'long_genwebid'
         and the appropriate value.
         The key for each target is their long_genwebid

        where the keys for an individual are:
            'OwnerID'
            'Surname'
            'Given' (a list of the given names)
            'Prefix'
            'Suffix'
            'Nickname'
            'IsPrimary'
            'BirthYear'
            'DeathYear'
            'FullName'

        This will create an hourglass html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database. Note that "person" is the same
        as person_facts['GenWebID']

        Given a person's PersonID (AKA OwnerID), the NameTable entry for that
        person.
        The form of spouse =
            [{'Surname': 'Page', 'OwnerID': '1', 'Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1953', 'Prefix': '',
              'DeathYear': '0', 'Sex':'male, 'GenWebID':'PageRobertK1953',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        spouses is a list of spouse NameTable entries

        Given a person's PersonID (AKA OwnerID) fetch the children's NameTable
        entries for that person.
        The fetch_person_from_ID return is of the form child =
            [{'Surname': 'Page', 'OwnerID': '1', 'Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1953', 'Prefix': '',
              'DeathYear': '0', 'Sex':'male, 'GenWebID':'PageRobertK1953',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        three_gen_family['child_list'] is a list of children NameTable entries

        father = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                    'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                    'Suffix': '', 'Surname': '', 'OwnerID': '',
                    'Sex': '', 'GenWebID': '', 'FullName': ''}
        mother = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                    'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                    'Suffix': '', 'Surname': '', 'OwnerID': '',
                    'Sex': '', 'GenWebID': '', 'FullName': ''}

        tgt_fathers_parents = {'Father': father, 'Mother': mother}
        """
        debug = False
        long_genwebid = family_dict["target"]["long_genwebid"]

        if long_genwebid == "-":
            debug = True

        if debug:
            print("line 1763 family_dict = ", family_dict)

        if long_genwebid in ["", "StoriesPersonal0000-"]:
            return

        short_genwebid_re = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9]{4}")
        person_facts = family_dict["target"]

        if "GenWebID" in family_dict["parents"]["mother"]:
            persons_mother = family_dict["parents"]["mother"]["GenWebID"]
        else:
            persons_mother = "-"

        if persons_mother == "":
            persons_mother = "-"

        hourglass_table = {}

        # Row 1
        hourglass_table[
            "c1r1"
        ] = '    <td align="center "><h2>Parents</h2></td><!--c1r1-->\n'
        hourglass_table[
            "c2r1"
        ] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c2r1-->\n'
        hourglass_table[
            "c3r1"
        ] = '    <td align="center ">&nbsp; &nbsp; &nbsp;</td><!--c3r1-->\n'
        hourglass_table[
            "c4r1"
        ] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c4r1-->\n'
        hourglass_table[
            "c5r1"
        ] = '    <td align="center "><h2>Person &amp; Spouse</h2></td><!--c5r1-->\n'
        hourglass_table[
            "c6r1"
        ] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c6r1-->\n'
        hourglass_table[
            "c7r1"
        ] = '    <td align="center ">&nbsp; &nbsp; &nbsp;</td><!--c7r1-->\n'
        hourglass_table[
            "c8r1"
        ] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c8r1-->\n'
        hourglass_table[
            "c9r1"
        ] = '    <td align="center "><h2>Children</h2></td><!--c9r1-->\n'

        for row in range(1, 21):  # insert start of rows <tr> and end of rows </tr>
            key = "c0r" + str(row)
            hourglass_table[key] = "  <tr><!--" + key + "-->\n"
            key = "c10r" + str(row)
            hourglass_table[key] = "  </tr><!--" + key + "-->\n"
        # pre-fill the table with blank info (empty table elements) -
        # these will be the default entries and will be replaced by people,
        # if they exist.
        for column in range(1, 10):
            for row in range(2, 21):
                key = "c" + str(column) + "r" + str(row)
                hourglass_table[key] = (
                    '    <td align="center "></td><!--' + key + "-->\n"
                )

        if "long_genwebid" not in person_facts:  # if person doesn't exist, return
            with open(
                folders_path + "/zzz_PeopleNotFound.txt", "a", encoding="utf-8"
            ) as not_found_file:
                not_found_file.write(
                    "*****BuildWebPages hourglass table row #1 ****** long_genwebid = \
                            "
                    + long_genwebid
                    + "\n"
                )

            return

        # c5r4 target person picture
        if os.path.isfile(
            folders_path + "/" + long_genwebid + "/" + long_genwebid + ".jpg"
        ):
            hourglass_table["c5r4"] = (
                '    <td align="center "><img src="../'
                + long_genwebid
                + "/"
                + long_genwebid
                + '.jpg" height="75"></td><!--c5r4-->\n'
            )
        else:
            hourglass_table[
                "c5r4"
            ] = '    <td align="center "><img src="../images/silhouette.jpg" \
                height="75"></td><!--c5r4-->\n'

        # c5r5 target person name and link
        hourglass_table["c5r5"] = (
            '    <td align="center "><a href=index.html><p>'
            + person_facts["FullName"]
            + "</p></a></td><!--c5r5-->\n"
        )

        # add parents (family_dict['parents'])
        #            Build father - possibilities are that:
        #                    - there is no father's name in the person's entry
        #                       - father's position empty and no link
        #                    - there is a father's name in the person's entry
        #                       - father's position (if no record, no name available)
        #                    - there is a record for the father
        #                       - father's position and link
        #                    - there is not a record for the father
        #                       - no father's position and no link
        # Need to do three things here
        # - if I have the person's name, use it
        # - if there is a person_id for the person, use it
        # - if neither, don't use maroon

        # preload the silhouette in case tgt parents have no photo
        hourglass_table[
            "c1r2"
        ] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r2-->\n'
        hourglass_table[
            "c1r3"
        ] = '    <td align="center "><p>unknown</p></a></td><!--c1r3-->\n'
        hourglass_table[
            "c2r3"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c2r3-->\n'
        hourglass_table[
            "c3r3"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c3r3-->\n'
        hourglass_table[
            "c3r4"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c3r4-->\n'
        hourglass_table[
            "c3r5"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'
        hourglass_table[
            "c4r5"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'
        hourglass_table[
            "c1r6"
        ] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r6-->\n'
        hourglass_table[
            "c1r7"
        ] = '    <td align="center "><p>unknown</p></a></td><!--c1r7-->\n'
        hourglass_table[
            "c2r7"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c2r7-->\n'
        hourglass_table[
            "c3r7"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c3r7-->\n'
        hourglass_table[
            "c3r6"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c3r6-->\n'
        hourglass_table[
            "c3r5"
        ] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'

        debug = False
        if long_genwebid == "-":
            debug = True
        if person_facts["OwnerID"] == "":
            debug = True

        if debug:
            print(
                "_generate_all_hourglass_webs line 1887 - long_genwebid = ",
                long_genwebid,
            )
            print("********* person_facts = ", person_facts)
            print("********* family_dict[parents] = ", family_dict["parents"])
            print("********* len(family_dict[parents]) = ", len(family_dict["parents"]))
        # Father
        if "OwnerID" in family_dict["parents"]["father"]:
            tgt_fathers_owner_id = family_dict["parents"]["father"]["OwnerID"]
            tgt_fathers_parents = rmagic.fetch_parents_from_id(
                self._tables["PersonTable"],
                self._tables["NameTable"],
                self._tables["FamilyTable"],
                tgt_fathers_owner_id,
            )
        else:
            fathers_mother_genwebid = "-"
            father = rmagic.empty_person()
            mother = rmagic.empty_person()
            tgt_fathers_parents = {"Father": father, "Mother": mother}

        if debug:
            print(
                "_generate_all_hourglass_webs line 1926 - long_genwebid = ",
                long_genwebid,
            )
            print("********* tgt_fathers_parents = ", tgt_fathers_parents)

        fathers_mother_genwebid = "-"
        if "GenWebID" not in family_dict["parents"]["father"] == "":
            fathers_mother_genwebid = "-"
        elif tgt_fathers_parents["Father"]["GenWebID"] != "":
            fathers_mother_genwebid = tgt_fathers_parents["Mother"]["GenWebID"]

        # handle the case where the fathers_mother_genwebid name is incomplete
        if fathers_mother_genwebid == "" or (
            not short_genwebid_re.match(fathers_mother_genwebid)
        ):
            fathers_mother_genwebid = "-"

        if "GenWebID" in family_dict["parents"]["father"]:  # father exists
            # c1r2 father picture
            if os.path.isfile(
                folders_path
                + "/"
                + family_dict["parents"]["father"]["GenWebID"]
                + fathers_mother_genwebid
                + "/"
                + family_dict["parents"]["father"]["GenWebID"]
                + fathers_mother_genwebid
                + ".jpg"
            ):
                hourglass_table["c1r2"] = (
                    '    <td align="center "><img src="../'
                    + family_dict["parents"]["father"]["GenWebID"]
                    + fathers_mother_genwebid
                    + "/"
                    + family_dict["parents"]["father"]["GenWebID"]
                    + fathers_mother_genwebid
                    + '.jpg" height="75"></td><!--c1r2-->\n'
                )
            else:
                if debug:
                    print(
                        "line 1954 - ",
                        folders_path
                        + "/"
                        + family_dict["parents"]["father"]["GenWebID"]
                        + fathers_mother_genwebid
                        + "/"
                        + family_dict["parents"]["father"]["GenWebID"]
                        + fathers_mother_genwebid
                        + ".jpg",
                    )
                hourglass_table[
                    "c1r2"
                ] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r2-->\n'

            # c1r3 target person name and link
            # was: if os.path.isdir(folders_path + "/" + three_gen_family['tgt_parents']['Father']["GenWebID"]): --- I don't want a link unless the index.html file exists
            if os.path.isfile(
                folders_path
                + "/"
                + family_dict["parents"]["father"]["GenWebID"]
                + fathers_mother_genwebid
                + "/index.html"
            ):
                hourglass_table["c1r3"] = (
                    '    <td align="center "><a href=../'
                    + family_dict["parents"]["father"]["GenWebID"]
                    + fathers_mother_genwebid
                    + "/index.html><p>"
                    + family_dict["parents"]["father"]["FullName"]
                    + "</p></a></td><!--c1r3-->\n"
                )
            else:
                hourglass_table["c1r3"] = (
                    '    <td align="center "><p>'
                    + family_dict["parents"]["father"]["FullName"]
                    + "</p></td><!--c1r3-->\n"
                )

            # c2r3 add arrow to select father as new target
            if os.path.isdir(
                folders_path
                + "/"
                + family_dict["parents"]["father"]["GenWebID"]
                + fathers_mother_genwebid
            ):
                hourglass_table["c2r3"] = (
                    '    <td align="center " bgcolor="maroon "><a href= ../'
                    + family_dict["parents"]["father"]["GenWebID"]
                    + fathers_mother_genwebid
                    + "/HourGlass.html><img src=../images/Left_Arrow.gif></a></td><!--c2r3-->\n"
                )
            else:
                hourglass_table[
                    "c2r3"
                ] = '    <td align="center " bgcolor="maroon "></td><!--c2r3-->\n'

            # c3r3 add maroon cell
            hourglass_table[
                "c3r3"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c3r3-->\n'

            # c3r4 add maroon cell
            hourglass_table[
                "c3r4"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c3r4-->\n'

            # c3r5 add maroon cell
            hourglass_table[
                "c3r5"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'

            # c4r5 add maroon cell
            hourglass_table[
                "c4r5"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'

        else:
            pass  # don't add any content if father doesn't exist

        if debug:
            print(
                "_generate_all_hourglass_webs line 1999 - long_genwebid= ",
                long_genwebid,
            )
            print("********* family_dict[parents] = ", family_dict["parents"])
            print("********* len(family_dict[parents]) = ", len(family_dict["parents"]))
            print("********* three_gen_family = ", family_dict)
        # Mother
        if "OwnerID" in family_dict["parents"]["mother"]:
            tgt_mothers_owner_id = family_dict["parents"]["mother"]["OwnerID"]
            tgt_mothers_parents = rmagic.fetch_parents_from_id(
                self._tables["PersonTable"],
                self._tables["NameTable"],
                self._tables["FamilyTable"],
                tgt_mothers_owner_id,
            )
        else:
            mothers_mother_genwebid = "-"
            father = rmagic.empty_person()
            mother = rmagic.empty_person()
            tgt_fathers_parents = {"Father": father, "Mother": mother}

        mothers_mother_genwebid = "-"
        if "GenWebID" not in family_dict["parents"]["mother"]:
            mothers_mother_genwebid = "-"
        elif "GenWebID" in tgt_mothers_parents["Mother"]:
            mothers_mother_genwebid = tgt_mothers_parents["Mother"]["GenWebID"]

        # handle the case where the mothers_mother_genwebid name is incomplete
        if mothers_mother_genwebid == "" or (
            not short_genwebid_re.match(mothers_mother_genwebid)
        ):
            mothers_mother_genwebid = "-"

        if "GenWebID" in family_dict["parents"]["mother"]:  # mother exists
            # c1r6 target person picture
            if os.path.isfile(
                folders_path
                + "/"
                + family_dict["parents"]["mother"]["GenWebID"]
                + mothers_mother_genwebid
                + "/"
                + family_dict["parents"]["mother"]["GenWebID"]
                + mothers_mother_genwebid
                + ".jpg"
            ):
                hourglass_table["c1r6"] = (
                    '    <td align="center "><img src="../'
                    + family_dict["parents"]["mother"]["GenWebID"]
                    + mothers_mother_genwebid
                    + "/"
                    + family_dict["parents"]["mother"]["GenWebID"]
                    + mothers_mother_genwebid
                    + '.jpg" height="75"></td><!--c1r6-->\n'
                )
            else:
                hourglass_table[
                    "c1r6"
                ] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r6-->\n'

            # c1r7 target person name and link
            # if os.path.isdir(folders_path + "/" + family_dict['parents']'Mother']["GenWebID"]): --- I don't want a link unless the index.html file exists
            if os.path.isfile(
                folders_path
                + "/"
                + family_dict["parents"]["mother"]["GenWebID"]
                + mothers_mother_genwebid
                + "/index.html"
            ):
                hourglass_table["c1r7"] = (
                    '    <td align="center "><a href=../'
                    + family_dict["parents"]["mother"]["GenWebID"]
                    + mothers_mother_genwebid
                    + "/index.html><p>"
                    + family_dict["parents"]["mother"]["FullName"]
                    + "</p></a></td><!--c1r7-->\n"
                )
            else:
                hourglass_table["c1r7"] = (
                    '    <td align="center "><p>'
                    + family_dict["parents"]["mother"]["FullName"]
                    + "</p></td><!--c1r7-->\n"
                )

            if debug:
                print("line 2068 - hourglass_table[c1r7] = ", hourglass_table["c1r7"])

            # c2r7 add arrow to select mother as new target
            if os.path.isdir(
                folders_path
                + "/"
                + family_dict["parents"]["mother"]["GenWebID"]
                + mothers_mother_genwebid
            ):
                hourglass_table["c2r7"] = (
                    '    <td align="center " bgcolor="maroon "><a href= ../'
                    + family_dict["parents"]["mother"]["GenWebID"]
                    + mothers_mother_genwebid
                    + "/HourGlass.html><img src=../images/Left_Arrow.gif></a></td><!--c2r7-->\n"
                )
            else:
                hourglass_table[
                    "c2r7"
                ] = '    <td align="center " bgcolor="maroon "></td><!--c2r7-->\n'

            # c3r7 add maroon cell
            hourglass_table[
                "c3r7"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c3r7-->\n'

            # c3r6 add maroon cell
            hourglass_table[
                "c3r6"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c3r6-->\n'

            # c3r5 add maroon cell
            hourglass_table[
                "c3r5"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'

            # c4r5 add maroon cell
            hourglass_table[
                "c4r5"
            ] = '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'

        else:
            pass  # don't add any content if mother doesn't exist

        # Spouses
        # Given a person's PersonID (AKA OwnerID), the NameTable entry
        spouse_list = family_dict["spouses"]

        row = 6
        debug = False

        if long_genwebid == "-":
            debug = True

        if debug:
            print("line 2112 - ********* spouse_list = ", spouse_list)
            print("********* len(spouse_list) = ", len(spouse_list))

        for spouse_num, spouse in enumerate(spouse_list):
            if debug:
                print("********* spouse_num = ", spouse_num)

            if not spouse and not short_genwebid_re.match(spouse["GenWebID"]):
                continue

            if debug:
                print(
                    "_generate_all_hourglass_webs line 2124 - spouse_num = ",
                    spouse_num,
                    "       spouse = ",
                    spouse,
                )

            spouses_parents = rmagic.fetch_parents_from_id(
                self._tables["PersonTable"],
                self._tables["NameTable"],
                self._tables["FamilyTable"],
                spouse["OwnerID"],
            )
            spouses_mothers_genwebid = spouses_parents["Mother"]["GenWebID"]
            # handle the case where the spouse's mother's name is incomplete
            if spouses_mothers_genwebid == "" or (
                not short_genwebid_re.match(spouses_mothers_genwebid)
            ):
                spouses_mothers_genwebid = "-"

            if debug:
                print(
                    "_generate_all_hourglass_webs line 2135 - spouses_mothers_genwebid = ",
                    spouses_mothers_genwebid,
                )

            # c5r6,8,10,12 target person picture
            if len(spouse) > 0:
                key = "c5r" + str(row)
                if debug:
                    print(
                        folders_path
                        + "/"
                        + spouse["GenWebID"]
                        + spouses_mothers_genwebid
                        + "/"
                        + spouse["GenWebID"]
                        + spouses_mothers_genwebid
                        + ".jpg"
                    )
                if os.path.isfile(
                    folders_path
                    + "/"
                    + spouse["GenWebID"]
                    + spouses_mothers_genwebid
                    + "/"
                    + spouse["GenWebID"]
                    + spouses_mothers_genwebid
                    + ".jpg"
                ):
                    hourglass_table[key] = (
                        '    <td align="center "><img src="../'
                        + spouse["GenWebID"]
                        + spouses_mothers_genwebid
                        + "/"
                        + spouse["GenWebID"]
                        + spouses_mothers_genwebid
                        + '.jpg" height="75"></td><!--'
                        + key
                        + "-->\n"
                    )
                    if debug:
                        print("hourglass_table[" + key + "] = ", hourglass_table[key])
                else:
                    hourglass_table[key] = (
                        '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--'
                        + key
                        + "-->\n"
                    )

                row = row + 1
                # c5r7,9,11,13 target person name and link
                key = "c5r" + str(row)
                hourglass_table[key] = (
                    '    <td align="center "><a href="../'
                    + spouse["GenWebID"]
                    + spouses_mothers_genwebid
                    + '/index.html"><p>'
                    + spouse["FullName"]
                    + "</p></a></td><!--"
                    + key
                    + "-->\n"
                )

                # c4r7,9,11,13 add arrow to select spouse as new target
                key = "c4r" + str(row)
                hourglass_table[key] = (
                    '    <td align="center"><a href= ../'
                    + spouse["GenWebID"]
                    + spouses_mothers_genwebid
                    + "/HourGlass.html><img src=../images/Right_Arrow_Maroon.gif></a></td><!--"
                    + key
                    + "-->\n"
                )
                if debug:
                    print("hourglass_table[" + key + "] = ", hourglass_table[key])
                row = row + 1

        # children
        # Given a person's PersonID (AKA OwnerID) fetch the children's NameTable
        child_list = family_dict["children"]

        row = 2
        debug = False
        if long_genwebid == "-":
            debug = True
        if debug:
            print("********* child_list = ", child_list)
            print("********* len(child_list) = ", len(child_list))
        for child_num, child in enumerate(child_list):
            if debug:
                print("********* child_num = ", child_num)

            if not child or not short_genwebid_re.match(child["GenWebID"]):
                continue

            if debug:
                print(
                    "_generate_all_hourglass_webs line 1437 - child_num = ",
                    child_num,
                    "       child = ",
                    child,
                )

            childs_long_genwebid = child["long_genwebid"]

            # c9r2, 4, 6, 8, ... 20 target person picture
            if child:
                key = "c9r" + str(row)
                if debug:
                    print(
                        folders_path
                        + "/"
                        + childs_long_genwebid
                        + "/"
                        + childs_long_genwebid
                        + ".jpg"
                    )
                if os.path.isfile(
                    folders_path
                    + "/"
                    + childs_long_genwebid
                    + "/"
                    + childs_long_genwebid
                    + ".jpg"
                ):
                    hourglass_table[key] = (
                        '    <td align="center "><img src="../'
                        + childs_long_genwebid
                        + "/"
                        + childs_long_genwebid
                        + '.jpg" height="75"></td><!--'
                        + key
                        + "-->\n"
                    )
                    if debug:
                        print("hourglass_table[" + key + "] = ", hourglass_table[key])
                else:
                    hourglass_table[key] = (
                        '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--'
                        + key
                        + "-->\n"
                    )

                # c7r4, 6, 8, ... 20 add maroon cell
                hourglass_table[
                    "c7r4"
                ] = '    <td align="center " bgcolor="maroon "></td><!--c7r4-->\n'
                if row > 2:
                    key = "c7r" + str(row)
                    hourglass_table[
                        key
                    ] = '    <td align="center " bgcolor="maroon "></td><!--c7r4, 6, 8, ... 20-->\n'

                row = row + 1
                # c9r3, 5, 7, ... 19 target person name and link
                key = "c9r" + str(row)
                hourglass_table[key] = (
                    '    <td align="center "><a href="../'
                    + childs_long_genwebid
                    + '/index.html"><p>'
                    + child["FullName"]
                    + "</p></a></td><!--"
                    + key
                    + "-->\n"
                )

                # c6r3 is always blank
                key = "c6r3"
                hourglass_table[key] = '    <td align="center"></td><!--c6r3-->\n'

                # c7r3, 5, 7, ... 19 add maroon cell
                key = "c7r" + str(row)
                hourglass_table[
                    key
                ] = '    <td align="center " bgcolor="maroon "></td><!--c7r3, 5, 7, ... 19-->\n'

                # c6r5 add maroon cell
                key = "c6r5"
                hourglass_table[
                    key
                ] = '    <td align="center " bgcolor="maroon "></td><!--c6r5-->\n'
                # c7r5 add maroon cell
                key = "c7r5"
                hourglass_table[
                    key
                ] = '    <td align="center " bgcolor="maroon "></td><!--c7r5-->\n'

                # c8r4, 6, 8, ... 20 add arrow to select child as new target
                key = "c8r" + str(row)
                hourglass_table[key] = (
                    '    <td align="center" bgcolor="maroon"><a href= ../'
                    + childs_long_genwebid
                    + "/HourGlass.html><img src=../images/Right_Arrow.gif></a></td><!--"
                    + key
                    + "-->\n"
                )
                if debug:
                    print("hourglass_table[" + key + "] = ", hourglass_table[key])
                row = row + 1

        # Build the web page
        # This builds the standard html header I use for the family history files
        # print('person = ', person, '  OwnerID = ', person_facts['OwnerID'])
        # print('person_facts = ', person_facts)
        hourglasshtml_list = []
        hourglasshtml_list.append("<html>\n")
        hourglasshtml_list.append("<head>\n")
        hourglasshtml_list.append(
            '    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />'
            + "\n"
        )

        # given_names = ''  -------------- not used - delete
        # for names in person_facts['Given']:
        #    given_names = given_names + ' ' + names

        hourglasshtml_list.append(
            "    <title>" + person_facts["FullName"] + "</title>" + "\n"
        )
        hourglasshtml_list.append(
            '    <link href="../css/individual.css" type="text/css" rel="stylesheet" />'
            + "\n"
        )
        hourglasshtml_list.append('    <style type="text/css">' + "\n")
        hourglasshtml_list.append("    /*<![CDATA[*/" + "\n")
        hourglasshtml_list.append(" div.ReturnToTop {text-align: right}" + "\n")
        hourglasshtml_list.append("    /*]]>*/" + "\n")
        hourglasshtml_list.append("    </style>\n")
        hourglasshtml_list.append("</head>\n")
        hourglasshtml_list.append('<body background="../images/back.gif">' + "\n")
        nickname = ""
        if len(person_facts["Nickname"]) > 1:
            nickname = ' "' + person_facts["Nickname"] + '" '
        build_string = (
            '    <h1><a name="Top"></a>' + person_facts["FullName"] + nickname
        )
        if debug:
            print(
                "\n line 943 _generate_all_hourglass_webs:  person_facts[BirthYear] = ",
                person_facts["BirthYear"],
                '     type(person_facts["BirthYear"]) = ',
                type(person_facts["BirthYear"]),
            )
        if person_facts["BirthYear"] == "":
            person_facts["BirthYear"] = "????"  # if not birth year then pass

        build_string = build_string + " - " + person_facts["BirthYear"]

        if debug:
            print(
                "\n line 949 _generate_all_hourglass_webs: person_facts[DeathYear] = ",
                person_facts["DeathYear"],
                '     type(person_facts["DeathYear"]) = ',
                type(person_facts["DeathYear"]),
            )

        if person_facts["DeathYear"] == "0":
            pass
        else:
            build_string = build_string + " - " + person_facts["DeathYear"]

        build_string = build_string + "</h1>\n"
        hourglasshtml_list.append(build_string)

        if persons_mother == "":
            persons_mother = "-"
        comment_string = (
            f'\t\t\t<p><a href="mailto:{self.admin_email}?subject='
            + long_genwebid
            + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: left; margin-right: auto" height="20"></a>\n'
        )
        hourglasshtml_list.append(comment_string)

        hourglasshtml_list.append(
            '<table border="0" cellspacing="0" cellpadding="0" align="center">\n'
        )
        # add the table to the HourGlass
        for row in range(1, 21):
            for column in range(0, 11):
                key = "c" + str(column) + "r" + str(row)
                hourglasshtml_list.append(hourglass_table[key])

        hourglasshtml_list.append("</table>")
        hourglasshtml_list.append("</body>")
        hourglasshtml_list.append("</html>")

        if os.path.isdir(folders_path + "/" + long_genwebid):
            with open(
                folders_path + "/" + long_genwebid + "/HourGlass.html",
                "w",
                encoding="utf-8",
            ) as hourglass_file:
                for row in hourglasshtml_list:  # commented out 1/22/2018 to minimize
                    hourglass_file.writelines(
                        row
                    )  # commented out 1/22/2018 to minimize

        else:
            with open(
                folders_path + "/zzz_FolderNotFound.txt", "a", encoding="utf-8"
            ) as folder_not_found:
                folder_not_found.write(
                    "***** _generate_all_hourglass_webs ****** folder = "
                    + long_genwebid
                    + "\n"
                )
                folder_not_found.write(
                    "person_facts[FullName] = "
                    + person_facts["FullName"]
                    + "\n person_facts[BirthYear] = "
                    + person_facts["BirthYear"]
                    + "\n person_facts[DeathYear] = "
                    + person_facts["DeathYear"]
                    + "\n"
                )

            # [{'Surname': 'Page', 'OwnerID': '1', 'Nickname': 'Bob',
            #  'Suffix': '', 'BirthYear': '1953', 'Prefix': '',
            #  'DeathYear': '0', 'Sex':'male, 'GenWebID':'PageRobertK1953',
            #  'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
            #  'FullName': 'Page, Robert Kenneth'}]
            # where these rootsmagic tags are equivalent ; OwnerID = person_ID)

        return  # end of _generate_all_hourglass_webs


# --------------------------------------------------


def main():
    """main entrypoint"""
    # Get the RootsMagic database info
    rmagic_path = sys.argv[1]
    web_folder = sys.argv[2]
    admin_email = sys.argv[3]
    BuildWebPages(rmagic_path, web_folder, admin_email)


if __name__ == "__main__":
    main()
