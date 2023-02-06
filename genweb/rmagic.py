#!/usr/bin/env python3

"""
Purpose: given a surname, given name, and date of birth, create a data
structure with the household
"""

import sqlite3
import fnmatch
import pickle
import logging
import contextlib
import re
from genweb import metaphone


_moduleLogger = logging.getLogger(__name__)


def _load_rmagic(rm_db):
    try:
        connection = sqlite3.connect(rm_db)
    except Exception:
        _moduleLogger.error("Failed with %s", rm_db)
        raise
    with contextlib.closing(connection) as connection:
        with contextlib.closing(connection.cursor()) as cursor:
            cursor.execute(
                "SELECT OwnerID, Surname, Given, Prefix, Suffix, \
                                    Nickname, IsPrimary, BirthYear, DeathYear \
                                    FROM NameTable"
            )
            name_tab = cursor.fetchall()

            print_name_table = True
            print_tables = False

            # Process NameTable
            name_dict = {}
            name_table = []
            ownerid_name_table = {}
            for name in name_tab:
                print_name_table = False
                print_tables = False
                if str(name[6]) != "1":
                    continue  # if not IsPrimary go to next name
                FullName = name[1] + ", " + name[2]
                given = name[2].split(" ")
                name_dict = {
                    "OwnerID": str(name[0]),
                    "Surname": name[1],
                    "Given": given,
                    "Prefix": name[3],
                    "Suffix": name[4],
                    "Nickname": name[5],
                    "IsPrimary": str(name[6]),
                    "BirthYear": str(name[7]),
                    "DeathYear": str(name[8]),
                    "FullName": FullName,
                }
                name_table.append(name_dict)
                if print_name_table:
                    print("name_dict =", name_dict)
                if name_dict["FullName"] == "":
                    print("name_dict =", name_dict)
                    print_name_table = True
                if (
                    len(name_dict["Surname"]) > 2 and len(name_dict["Given"][0]) > 1
                ):  # changed from 2 to 1 20160623
                    ownerid_name_table[name_dict["OwnerID"]] = name_dict
                    if print_name_table:
                        print("name_dict =", str(name_dict))
                if print_name_table:
                    print(
                        "name_table name_dict = ",
                        name_dict["OwnerID"],
                        ",",
                        name_dict["Surname"],
                        ",",
                        name_dict["Given"],
                        ",",
                        name_dict["Prefix"],
                        ",",
                        name_dict["Suffix"],
                        ",",
                        name_dict["Nickname"],
                        ",",
                        name_dict["IsPrimary"],
                        ",",
                        name_dict["BirthYear"],
                        ",",
                        name_dict["DeathYear"],
                    )

            # Process PersonTable
            cursor.execute(
                "SELECT PersonID,Sex,ParentID,\
                            SpouseID FROM PersonTable"
            )
            person_tab = cursor.fetchall()
            person_dict = {}
            person_table = []
            person_id_person_table = {}
            for person in person_tab:
                person_dict = {
                    "PersonID": str(person[0]),
                    "Sex": str(person[1]),
                    "ParentID": str(person[2]),
                    "SpouseID": str(person[3]),
                }
                person_table.append(person_dict)
                person_id_person_table[person_dict["PersonID"]] = person_dict
                if print_tables:
                    print("person_table person_dict = ", str(person_dict))

            # Process ChildTable
            cursor.execute("SELECT ChildID,FamilyID,ChildOrder FROM ChildTable")
            child_tab = cursor.fetchall()
            child_dict = {}
            child_table = []
            for child in child_tab:
                child_dict = {
                    "ChildID": str(child[0]),
                    "FamilyID": str(child[1]),
                    "ChildOrder": str(child[2]),
                }
                child_table.append(child_dict)
                if print_tables:
                    print("child_table child_dict = ", str(child_dict))

            # Process FamilyTable
            cursor.execute(
                "SELECT FamilyID,FatherID,MotherID,\
                            ChildID FROM FamilyTable"
            )
            family_tab = cursor.fetchall()
            family_dict = {}
            family_table = []
            family_id_family_table = {}
            for family in family_tab:
                family_dict = {
                    "FamilyID": str(family[0]),
                    "FatherID": str(family[1]),
                    "MotherID": str(family[2]),
                    "ChildID": str(family[3]),
                }
                family_table.append(family_dict)
                family_id_family_table[family_dict["FamilyID"]] = family_dict
                if print_tables:
                    print("family_table family_dict = ", str(family_dict))

    roots_magic_db = {
        "NameTable": name_table,
        "PersonTable": person_table,
        "ChildTable": child_table,
        "FamilyTable": family_table,
        "ownerid_name_table": ownerid_name_table,
        "person_id_person_table": person_id_person_table,
        "family_id_family_table": family_id_family_table,
    }
    return roots_magic_db


def fetch_rm_tables(rm_db):
    """
    Read the RootsMagic database table
    @returns roots_magic_db{
        'NameTable':name_table,
        'PersonTable':person_table
        'ChildTable':child_table,
        'FamilyTable':family_table
        'ownerid_name_table': ownerid_name_table,
        'personid_name_table': personid_name_table,
        'familyid_table': familyid_table
    }
    where each table is a list of the table rows
    where each row is a dict for that row.
    each *id*_table is a dictionary of dictionaries where the top level keys
    are each *id
    """
    cache_path = "pickle_rm_db.pkl"
    # TODO: Add support for loading the cache
    if False:
        with open(cache_path, "bb") as f:
            roots_magic_db = pickle.load(f)
    else:
        roots_magic_db = _load_rmagic(rm_db)
        with open(cache_path, "wb") as f:
            pickle.dump(roots_magic_db, f)

    return roots_magic_db


def fetch_person_from_name(name_table, person_table, name_dict):
    """
    Given a person's 'Surname', 'Given', 'Initial', 'BirthYear' fetch the NameTable entry
    for that person. If there is more than one match, they will all be returned
    The return is of the form:
        [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
          'Suffix': '', 'BirthYear': '1949','Prefix': '',
          'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
          'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
          'FullName': 'Page, Robert Kenneth'}]
        where these rootsmagic tags are equivalent ; OwnerID = person_ID
    """

    debug = False
    if (
        name_dict["Surname"]
        + name_dict["Given"]
        + name_dict["Initial"]
        + name_dict["BirthYear"]
        == ""
    ):
        debug = True
    if debug == True:
        fetch_person_from_name_file = open(
            "C:\Family_History\FamilyHistoryWeb\Individual_Web_Pages/zzzRM_fetch_person_from_name.txt",
            "a",
        )
        fetch_person_from_name_file.write("entering fetch_person_from_name:\n")
        fetch_person_from_name_file.write(
            "line 149 - name_dict[Surname] = " + name_dict["Surname"] + "\n"
        )
        fetch_person_from_name_file.write(
            "line 150 - name_dict[Given] = " + name_dict["Given"] + "\n"
        )
        fetch_person_from_name_file.write(
            "line 151 - name_dict[BirthYear] = " + name_dict["BirthYear"] + "\n"
        )
        fetch_person_from_name_file.close()

    if name_dict["Given"] == "" and name_dict["BirthYear"] == "" and debug:
        print("0---fetch_person_from_name--- name_dict = ", name_dict)
        debug = False
    person_matches = []
    # if debug: print('name_table = ', name_table)
    for person in name_table:  # only testing their first middle initial, if it exists
        if person["Surname"] == "":
            continue
        if len(person["Given"]) == 1:
            person["Given"].append("")
        if name_dict["BirthYear"] == "":
            name_dict["BirthYear"] = "0000"
        if all(
            (
                person["Surname"].replace(" ", "")
                == name_dict["Surname"].replace(" ", ""),
                person["Given"][0] == name_dict["Given"],
                person["Given"][1][0:1] == name_dict["Initial"][0:1],
                int(person["BirthYear"]) == int(name_dict["BirthYear"]),
                person["IsPrimary"] == "1",
            )
        ):
            person["Surname"] = person["Surname"].replace(" ", "")
            if debug == True:
                fetch_person_from_name_file = open(
                    "C:\Family_History\FamilyHistoryWeb\Individual_Web_Pages/zzzRM_fetch_person_from_name.txt",
                    "a",
                )
                fetch_person_from_name_file.write(
                    "\n \n line 174 - name_dict = " + str(name_dict) + "\n"
                )
                fetch_person_from_name_file.write(
                    "1---fetch_person_from_name--- match person = \n"
                )
                fetch_person_from_name_file.write(
                    "line 176 - person[Surname] = " + person["Surname"] + "\n"
                )
                fetch_person_from_name_file.write(
                    "line 177 - person[Given] = " + person["Given"][0] + "\n"
                )
                fetch_person_from_name_file.write(
                    "line 178 - person[BirthYear] = " + person["BirthYear"] + "\n"
                )
                fetch_person_from_name_file.close()

            for target in person_table:
                if target["PersonID"] == person["OwnerID"]:
                    if debug == True:
                        fetch_person_from_name_file = open(
                            "C:\Family_History\FamilyHistoryWeb\Individual_Web_Pages/zzzRM_fetch_person_from_name.txt",
                            "a",
                        )
                        fetch_person_from_name_file.write(
                            "---fetch_person_from_name--- target =\n"
                        )
                        fetch_person_from_name_file.write(
                            "line 186 - target[PersonID] = " + target["PersonID"] + "\n"
                        )
                        fetch_person_from_name_file.write(
                            "line 187 - target[ParentID] = "
                            + str(target["ParentID"])
                            + "\n"
                        )
                        fetch_person_from_name_file.write(
                            "line 188 - target[SpouseID] = " + target["SpouseID"] + "\n"
                        )
                        fetch_person_from_name_file.close()
                    person["Sex"] = "male" if target["Sex"] == "0" else "female"
                    break

            names = ""
            for name in person["Given"]:
                names = names + " " + name
            person["FullName"] = person["Surname"] + "," + names

            genweb_id = person["Surname"]
            for given_num in range(len(person["Given"])):
                if debug == True:
                    fetch_person_from_name_file = open(
                        "C:\Family_History\FamilyHistoryWeb\Individual_Web_Pages/zzzRM_fetch_person_from_name.txt",
                        "a",
                    )
                    fetch_person_from_name_file.write(
                        "---fetch_person_from_name line 203--- genweb_id = "
                        + genweb_id
                        + "\n"
                    )
                    fetch_person_from_name_file.write(
                        "---fetch_person_from_name line 204--- person[Given][given_num] = "
                        + person["Given"][given_num]
                        + "\n"
                    )
                    fetch_person_from_name_file.write(
                        "---fetch_person_from_name line 205--- given_num = "
                        + str(given_num)
                        + "\n"
                    )
                    fetch_person_from_name_file.close()
                if given_num == 0:
                    genweb_id = genweb_id + person["Given"][0]
                elif given_num == 1:
                    genweb_id = genweb_id + person["Given"][given_num][0:1]
                elif given_num == 2:
                    genweb_id = genweb_id + person["Given"][given_num][0:1]
                elif given_num == 3:
                    genweb_id = genweb_id + person["Given"][given_num][0:1]
            genweb_id = genweb_id.strip(".")

            if debug == True:
                fetch_person_from_name_file = open(
                    "C:\Family_History\FamilyHistoryWeb\Individual_Web_Pages/zzzRM_fetch_person_from_name.txt",
                    "a",
                )
                fetch_person_from_name_file.write(
                    "fetch_person_from_name line 219--- person[BirthYear] = "
                    + person["BirthYear"]
                    + "\n"
                )
                fetch_person_from_name_file.close()
            if person["BirthYear"] == "0":
                person["BirthYear"] = "0000"
            if len(person["BirthYear"]) == 3:
                person["BirthYear"] = "0" + person["BirthYear"]
                if debug == True:
                    fetch_person_from_name_file = open(
                        "C:\Family_History\FamilyHistoryWeb\Individual_Web_Pages/zzzRM_fetch_person_from_name.txt",
                        "a",
                    )
                    fetch_person_from_name_file.write(
                        "fetch_person_from_name line 227--- 3 digit corrected person[BirthYear] = "
                        + person["BirthYear"]
                        + "\n"
                    )
                    fetch_person_from_name_file.close()

            genweb_id = genweb_id + person["BirthYear"]
            person["GenWebID"] = genweb_id

            person_matches.append(person)

            if debug == True:
                fetch_person_from_name_file = open(
                    "C:\Family_History\FamilyHistoryWeb\Individual_Web_Pages/zzzRM_fetch_person_from_name.txt",
                    "a",
                )
                fetch_person_from_name_file.write(
                    "\n \n 2---exiting fetch_person_from_name:--- person_matches = \n"
                )
                for person in person_matches:
                    fetch_person_from_name_file.write(
                        " line 239 - person[Surname] = " + person["Surname"] + "\n"
                    )
                    fetch_person_from_name_file.write(
                        " line 240 - person[Given] = " + person["Given"][0] + "\n"
                    )
                    fetch_person_from_name_file.write(
                        " line 241 - person[BirthYear] = " + person["BirthYear"] + "\n"
                    )
                fetch_person_from_name_file.close()

    if debug and not person_matches:
        print(
            "3---exiting fetch_person_from_name---no match found - name_dict = ",
            name_dict,
        )

    if not person_matches:
        _moduleLogger.debug("No person found: %r", name_dict)
    return person_matches


def fetch_person_from_fuzzy_name(name_table, name_dict, year_error=2):
    """
    Given a person's 'Surname', 'Given', 'BirthYear' fetch the NameTable entry
    for that person. If there is more than one match, they will all be returned
    """
    person_matches = []
    for person in name_table:
        person_sur = metaphone.dm(person["Surname"].replace(" ", ""))[0]
        name_dict_sur = metaphone.dm(name_dict["Surname"])[0]
        person_given = metaphone.dm(person["Given"][0])[0]
        name_dict_given = metaphone.dm(name_dict["Given"])[0]
        try:
            birth_error = abs(int(person["BirthYear"]) - int(name_dict["BirthYear"]))
        except ValueError:
            # RootsMagic sets the birthyear to zero if a birthyear isn't given
            # if the search parameter is '????' and the birthyear is zero,
            # I want to set the equal to '0000'
            if person["BirthYear"] == "0":
                match_birthyear = "0000"
            else:
                match_birthyear = person["BirthYear"]

            years_match = fnmatch.fnmatch(match_birthyear, name_dict["BirthYear"])
        else:
            years_match = birth_error <= year_error
        if all(
            (
                person_sur == name_dict_sur,
                person_given == name_dict_given,
                years_match,
                person["IsPrimary"] == "1",
            )
        ):
            person_matches.append(person)

    if not person_matches:
        _moduleLogger.debug("No person found: %r", name_dict)
    return person_matches


def fetch_person_from_ID2(
    ownerid_name_table, personid_name_table, id
):  # attempt at rewrite of fetch_person_from_ID
    """
    Given a person's PersonID (AKA OwnerID) fetch the NameTable entry for that
    person.
    The return is of the form:
        [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
          'Suffix': '', 'BirthYear': '1949','Prefix': '',
          'DeathYear': '0', 'Sex':'male,'long_genwebid':'PageRobertK1949HughsMarillynH1925',
          'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
          'FullName': 'Page, Robert Kenneth'}]
    """

    debug = False
    if name_dict["OwnerID"] == "":
        debug = True

    name_dict = ownerid_name_table[id]
    """
    where name_dict = { 'OwnerID': str(name[0]),
                        'Surname': name[1],
                        'Given': given,
                        'Prefix': name[3],
                        'Suffix': name[4],
                        'Nickname': name[5],
                        'IsPrimary': str(name[6]),
                        'BirthYear': str(name[7]),
                        'DeathYear': str(name[8])}
    """

    person_sex = (
        "male" if personid_name_table[name_dict["OwnerID"]]["Sex"] == "0" else "female"
    )

    if name_dict["BirthYear"] == "0":
        birth_year = "0000"
    elif len(name_dict["BirthYear"]) == 3:
        birth_year = "0" + name_dict["BirthYear"]
    else:
        birth_year = person["BirthYear"]

    genweb_id = name_dict["Surname"]

    for given_num in range(len(name_dict["Given"])):
        if given_num == 0 and len(name_dict["Given"][0]) <= 2:
            return {}
        if given_num == 0:
            genweb_id = genweb_id + name_dict["Given"][0]
            if debug == True:
                print("genweb_id1 = ", genweb_id)
        else:
            if debug == True:
                print("given_num = ", given_num)
            if len(name_dict["Given"][given_num]) > 0:
                genweb_id = genweb_id + name_dict["Given"][given_num][0]
            if debug == True:
                print("genweb_id2 = ", genweb_id)

    genweb_id = genweb_id.strip(".")  # this is the short genweb_id

    result = {
        "OwnerID": name_dict["OwnerID"],
        "Surname": name_dict["Surname"],
        "Given": name_dict["Given"],
        "Prefix": name_dict["Prefix"],
        "Suffix": name_dict["Suffix"],
        "Nickname": name_dict["Nickname"],
        "IsPrimary": name_dict["IsPrimary"],
        "BirthYear": name_dict["BirthYear"],
        "DeathYear": name_dict["DeathYear"],
        "Sex": person_sex,
        "FullName": name_dict["Surname"] + ", " + name_dict["Given"],
        "GenWebID": genweb_id,
    }
    return result


def fetch_person_from_ID(name_table, person_table, id):
    """
    Given a person's PersonID (AKA OwnerID) fetch the NameTable entry for that
    person.
    The return is of the form:
        [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
          'Suffix': '', 'BirthYear': '1949','Prefix': '',
          'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
          'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
          'FullName': 'Page, Robert Kenneth'}]
    """
    debug = False
    if id == "":
        debug = True
    for person in name_table:
        if person["OwnerID"] == id and person["IsPrimary"] == "1":
            if debug == True:
                print("fetch_person_from_ID person = ", person)
            for target in person_table:
                if target["PersonID"] == person["OwnerID"]:
                    person["Sex"] = "male" if target["Sex"] == "0" else "female"
                    break

            names = ""
            for name in person["Given"]:
                names = names + " " + name
            person["FullName"] = person["Surname"] + "," + names

            if len(person["Surname"]) <= 3:
                return {}
            genweb_id = person["Surname"]

            if debug == True:
                print("genweb_id0 = ", genweb_id)
            for given_num in range(len(person["Given"])):
                if given_num == 0 and len(person["Given"][0]) <= 2:
                    return {}
                if given_num == 0:
                    genweb_id = genweb_id + person["Given"][0]
                    if debug == True:
                        print("genweb_id1 = ", genweb_id)
                else:
                    if debug == True:
                        print("given_num = ", given_num)
                    if len(person["Given"][given_num]) > 0:
                        genweb_id = genweb_id + person["Given"][given_num][0]
                    if debug == True:
                        print("genweb_id2 = ", genweb_id)

            genweb_id = genweb_id.strip(".")

            if person["BirthYear"] == "0":
                birth_year = "0000"
            elif len(person["BirthYear"]) == 3:
                birth_year = "0" + person["BirthYear"]
            else:
                birth_year = person["BirthYear"]

            genweb_id = genweb_id + birth_year
            person["GenWebID"] = genweb_id
            if debug == True:
                print("person = ", person)
                print("++++++++++++++++++++++++++++++++++++++")
            return person
    else:
        _moduleLogger.debug("Person not found: %r", id)
        return {}


def fetch_sex_from_ID(person_table, person_ID):
    # Owner_ID in the name_table points to
    person_sex = ""
    for person in person_table:
        if person["PersonID"] == person_ID:
            person_sex = "male" if person["Sex"] == 0 else "female"
            break
    return person_sex


def fetch_parents_from_ID(person_table, name_table, family_table, person_ID):
    """
    Given a target person's PersonID (OwnerID in name_table)
    1. fetch the ParentID (FamilyID in family_table) from the person_table
    2. using the ParentID as the Family_ID fetch the FatherID & MotherID from
        the Family_Table
    3. using the FatherID & MotherID as the name_table OwnerID fetch the
        parents from the NameTable
    """
    for person in person_table:
        if person["PersonID"] == person_ID:
            break
    else:
        parent_ID = ""
        person = {}
    parent_ID = person.get("ParentID", "")
    for family in family_table:
        if parent_ID == family["FamilyID"]:
            father_ID = family["FatherID"]
            mother_ID = family["MotherID"]
            break
    else:
        father_ID = ""
        mother_ID = ""

    father = fetch_person_from_ID(name_table, person_table, father_ID)
    mother = fetch_person_from_ID(name_table, person_table, mother_ID)

    if father == {}:
        father = {
            "Given": [""],
            "IsPrimary": "1",
            "DeathYear": "",
            "Prefix": "",
            "BirthYear": "",
            "Nickname": "",
            "Suffix": "",
            "Surname": "",
            "OwnerID": "",
            "Sex": "",
            "GenWebID": "",
            "FullName": "",
        }
    if mother == {}:
        mother = {
            "Given": [""],
            "IsPrimary": "1",
            "DeathYear": "",
            "Prefix": "",
            "BirthYear": "",
            "Nickname": "",
            "Suffix": "",
            "Surname": "",
            "OwnerID": "",
            "Sex": "",
            "GenWebID": "",
            "FullName": "",
        }

    parents = {"Father": father, "Mother": mother}

    return parents


def fetch_family_from_ID(person_table, family_table, person_ID):
    """
    Given a target person's PersonID (OwnerID in name_table)
        1. get the person's Sex from the PersonTable by searching the personID
        2. fetch the family info from the family_table
    """
    male = "0"
    female = "1"
    spouses = []

    for person in person_table:
        if person["PersonID"] == person_ID:
            break
    else:
        print(
            "rmagic.py - fetch_family_from_ID -  no person in the person_table matches person_ID = ",
            person_ID,
        )
        parent_ID = ""
        person = {}
    sex = person.get("Sex", male)
    for family in family_table:
        if sex == male and family["FatherID"] == person_ID:
            yield family, "FatherID"
        elif sex == female and family["MotherID"] == person_ID:
            yield family, "MotherID"


def fetch_spouses_from_ID(name_table, person_table, family_table, person_ID):
    """
    Given a target person's PersonID (OwnerID in name_table)
        1. get the person's Sex from the PersonTable by searching the personID
        2. fetch the spouse IDs from the family_table
        3. using the spouse IDs fetch the spouse(s) info from the NameTable
    """
    spouses = []
    for family, parentalRole in fetch_family_from_ID(
        person_table, family_table, person_ID
    ):
        spousalRole = "MotherID" if parentalRole == "FatherID" else "FatherID"
        spouse_id = family[spousalRole]

        spouses.append(fetch_person_from_ID(name_table, person_table, spouse_id))
        """
        Given a person's PersonID (AKA OwnerID) fetch the NameTable entry for that
        person.
        The fetch_person_from_ID return is of the form spouse =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        """
    return spouses  # a list of spouse NameTable entries


def fetch_children_from_ID(
    child_table, name_table, person_table, family_table, person_ID
):
    """
    Given a target person's PersonID (OwnerID in name_table)
        1. get the person's Sex from the PersonTable by searching the personID
        2. fetch the FamilyID from the family_table
        3. using the FamilyID fetch the ChildID for each child in the
            ChildTable
        4. Using the ChildID as the OwnerID get each child's info from
            NameTable
    """
    children = []

    for family, parentalRole in fetch_family_from_ID(
        person_table, family_table, person_ID
    ):
        family_id = family["FamilyID"]
        for child in child_table:
            if family_id == child["FamilyID"]:
                children.append(
                    fetch_person_from_ID(name_table, person_table, child["ChildID"])
                )
    return children


def build_given_name(given):
    """
    >>> build_given_name(["Mary", "Jo"])
    'Mary J'
    """
    namestring = ""
    for names in given:
        if not namestring:
            namestring = names
        else:
            namestring += " " + names[0]
    return namestring


if __name__ == "__main__":
    import doctest

    print(doctest.testmod())
