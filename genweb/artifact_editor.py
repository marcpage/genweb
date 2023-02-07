#!/usr/bin/env python3

import datetime
import os
import re
import sys

import tkinter
from tkinter import *
from tkinter import ttk

from genweb import rmagic


class Editor(object):
    _MAX_MATCHES_VISIBLE = 6
    _MAX_TARGET_FAMILIES_VISIBLE = 22
    _MAX_PEOPLE_REFERENCED = 26

    def __init__(self, rmagicPath):
        self._rmagicPath = rmagicPath
        self._tables = rmagic.fetch_rm_tables(self._rmagicPath)

        self._matched_persons = []

        self._root = Tk()
        self._root.title("Family History: Enter a Person")

        style = ttk.Style()
        try:
            style.theme_use("vista")
        except Exception:
            _moduleLogger.debug("Theme unsupported")

        mainframe = ttk.Frame(
            self._root,
            borderwidth=5,
            relief="sunken",
            width=200,
            height=100,
            padding="12 12 12 12",
        )

        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        # Search boxes
        self._srch_person = {
            "Given": StringVar(),
            "Surname": StringVar(),
            "BirthYear": StringVar(),
        }
        self._srch_person["Given"].set("")
        self._srch_person["Surname"].set("")
        self._srch_person["BirthYear"].set("????")

        # Found person labels
        self._match = []
        for m_no in range(self._MAX_MATCHES_VISIBLE):
            self._match.append(
                {
                    "Given": StringVar(),
                    "Surname": StringVar(),
                    "BirthYear": StringVar(),
                }
            )
            for f in self._match[m_no]:
                self._match[m_no][f].set("-")

        # Radiobutton person selector
        self._selected_person = StringVar()

        # Target family labels
        # checkbox include person - the variable is set to 1 if the button is
        # selected, and 0 otherwise.
        self._tgt_family = []
        for tf_no in range(self._MAX_TARGET_FAMILIES_VISIBLE):
            self._tgt_family.append(
                {
                    "Check": StringVar(),
                    "Given": StringVar(),
                    "Surname": StringVar(),
                    "BirthYear": StringVar(),
                    "DeathYear": StringVar(),
                    "ID": StringVar(),
                }
            )
            self._tgt_family[tf_no]["Given"].set("-")
            self._tgt_family[tf_no]["Surname"].set("-")
            self._tgt_family[tf_no]["BirthYear"].set("-")
            self._tgt_family[tf_no]["DeathYear"].set("-")
            self._tgt_family[tf_no]["ID"].set("-")

        # target person - self._tgt_family index = 0
        # father of target - self._tgt_family index = 1
        # mother of target - self._tgt_family index = 2
        # spouses of target - self._tgt_family index = 3-6
        # children of target - self._tgt_family index = 7-21

        # set up the people referenced table
        self._ppl = []
        for ppl_no in range(self._MAX_PEOPLE_REFERENCED):
            self._ppl.append(
                {
                    "Check": StringVar(),
                    "Given": StringVar(),
                    "Surname": StringVar(),
                    "BirthYear": StringVar(),
                    "DeathYear": StringVar(),
                    "ID": StringVar(),
                }
            )
            self._ppl[ppl_no]["Given"].set("-")
            self._ppl[ppl_no]["Surname"].set("-")
            self._ppl[ppl_no]["BirthYear"].set("-")
            self._ppl[ppl_no]["DeathYear"].set("-")
            self._ppl[ppl_no]["ID"].set("-")

        # File Generation labels
        self._file_gen = {
            "Header": StringVar(),
            "Artifact_ID_Label": StringVar(),
            "Artifact_ID": StringVar(),
            "Artifact_Title_Label": StringVar(),
            "Artifact_Title": StringVar(),
            "Artifact_Caption_Label": StringVar(),
            "Artifact_Caption": StringVar(),
            "Artifact_Misc_Label": StringVar(),
            "Artifact_Misc": StringVar(),
            "Artifact_Path_Label": StringVar(),
            "Artifact_Path": StringVar(),
        }

        # Define the rows
        current_row = 1
        ttk.Label(mainframe, text="1st Given Name").grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, text="Surname   ").grid(
            column=4, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, text="Birth").grid(column=5, row=current_row, sticky=EW)
        colmSep1 = ttk.Separator(mainframe, orient=VERTICAL)
        colmSep1.grid(column=8, row=current_row, rowspan="35", sticky="ns")
        colmSep2 = ttk.Separator(mainframe, orient=VERTICAL)
        colmSep2.grid(column=9, row=current_row, rowspan="35", sticky="ns")
        ttk.Label(mainframe, textvariable=self._file_gen["Header"]).grid(
            column=11, row=current_row, sticky=EW, columnspan=5
        )

        current_row = 2
        ttk.Button(mainframe, text="Search", command=self._on_search_for_matches).grid(
            column=1, row=2, sticky=W, columnspan=1, rowspan=1
        )
        ttk.Entry(mainframe, width=7, textvariable=self._srch_person["Given"]).grid(
            column=3, row=current_row, sticky=(W, E), columnspan=1
        )
        ttk.Entry(mainframe, width=7, textvariable=self._srch_person["Surname"]).grid(
            column=4, row=current_row, sticky=(W, E), columnspan=1
        )
        ttk.Entry(mainframe, width=7, textvariable=self._srch_person["BirthYear"]).grid(
            column=5, row=current_row, sticky=(W, E), columnspan=1
        )

        current_row = 3
        titleSep1 = ttk.Separator(mainframe, orient=HORIZONTAL)
        titleSep1.grid(column=0, row=current_row, columnspan="16", sticky="we")

        current_row = 4
        ttk.Button(
            mainframe,
            text="View\nPossible\nMatch",
            command=self._on_view_possible_person,
        ).grid(column=1, row=current_row, sticky=W, columnspan=1, rowspan=3)
        ttk.Radiobutton(
            mainframe, text="", variable=self._selected_person, value="0"
        ).grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[0]["Given"]).grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[0]["Surname"]).grid(
            column=4, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[0]["BirthYear"]).grid(
            column=5, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_ID_Label"]).grid(
            column=10, row=current_row, sticky=EW, columnspan=2
        )
        ttk.Entry(mainframe, width=10, textvariable=self._file_gen["Artifact_ID"]).grid(
            column=12, row=current_row, sticky=W, columnspan=3
        )

        current_row = 5
        ttk.Radiobutton(
            mainframe, text="", variable=self._selected_person, value="1"
        ).grid(column=2, row=5, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[1]["Given"]).grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[1]["Surname"]).grid(
            column=4, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[1]["BirthYear"]).grid(
            column=5, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_Title_Label"]).grid(
            column=10, row=current_row, sticky=EW
        )
        ttk.Entry(
            mainframe, width=7, textvariable=self._file_gen["Artifact_Title"]
        ).grid(column=11, row=current_row, sticky=(W, E), columnspan=6)

        current_row = 6
        ttk.Radiobutton(
            mainframe, text="", variable=self._selected_person, value="2"
        ).grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[2]["Given"]).grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[2]["Surname"]).grid(
            column=4, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[2]["BirthYear"]).grid(
            column=5, row=current_row, sticky=EW
        )
        ttk.Label(
            mainframe, textvariable=self._file_gen["Artifact_Caption_Label"]
        ).grid(column=10, row=current_row, sticky=EW)
        ttk.Entry(
            mainframe, width=45, textvariable=self._file_gen["Artifact_Caption"]
        ).grid(column=11, row=current_row, sticky=NS, columnspan=6, rowspan=1)

        current_row = 7
        ttk.Button(
            mainframe,
            text="Add to\nPeople\nReferenced",
            command=self._on_add_to_people_ref,
        ).grid(column=1, row=current_row, sticky=W, columnspan=1, rowspan=3)
        ttk.Radiobutton(
            mainframe, text="", variable=self._selected_person, value="3"
        ).grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[3]["Given"]).grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[3]["Surname"]).grid(
            column=4, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[3]["BirthYear"]).grid(
            column=5, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_Misc_Label"]).grid(
            column=10, row=current_row, sticky=EW
        )
        ttk.Entry(
            mainframe, width=45, textvariable=self._file_gen["Artifact_Misc"]
        ).grid(column=11, row=current_row, sticky=NS, columnspan=6, rowspan=1)

        current_row = 8
        ttk.Radiobutton(
            mainframe, text="", variable=self._selected_person, value="4"
        ).grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[4]["Given"]).grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[4]["Surname"]).grid(
            column=4, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[4]["BirthYear"]).grid(
            column=5, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_Path_Label"]).grid(
            column=10, row=current_row, sticky=EW
        )
        ttk.Entry(
            mainframe, width=45, textvariable=self._file_gen["Artifact_Path"]
        ).grid(column=11, row=current_row, sticky=NS, columnspan=6, rowspan=1)

        current_row = 9
        ttk.Radiobutton(
            mainframe, text="", variable=self._selected_person, value="5"
        ).grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[5]["Given"]).grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[5]["Surname"]).grid(
            column=4, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, textvariable=self._match[5]["BirthYear"]).grid(
            column=5, row=current_row, sticky=EW
        )

        current_row = 10
        titleSep2 = ttk.Separator(mainframe, orient=HORIZONTAL)
        titleSep2.grid(column=0, row=current_row, columnspan="8", sticky="we")
        ttk.Label(mainframe, text="Given Names").grid(
            column=11, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, text="Surname").grid(column=12, row=current_row, sticky=EW)
        ttk.Label(mainframe, text="Birth").grid(column=13, row=current_row, sticky=EW)
        ttk.Label(mainframe, text="Death").grid(column=14, row=current_row, sticky=EW)
        ttk.Label(mainframe, text="ID#").grid(column=15, row=current_row, sticky=EW)

        current_row = 11
        ttk.Label(mainframe, text="Matching Person Details").grid(
            column=3, row=current_row, columnspan="3", sticky=EW
        )
        ttk.Label(mainframe, text="People").grid(column=10, row=current_row, sticky=EW)

        current_row = 12
        ttk.Label(mainframe, text="Given Names").grid(
            column=3, row=current_row, sticky=EW
        )
        ttk.Label(mainframe, text="Surname").grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, text="Birth").grid(column=5, row=current_row, sticky=EW)
        ttk.Label(mainframe, text="Death").grid(column=6, row=current_row, sticky=EW)
        ttk.Label(mainframe, text="ID#").grid(column=7, row=current_row, sticky=EW)
        ttk.Label(mainframe, text="Referenced").grid(
            column=10, row=current_row, sticky=EW
        )

        current_row = 13
        ttk.Label(mainframe, text="Search Target").grid(
            column=1, row=current_row, sticky=EW
        )

        for current_row in range(13, 35):
            ttk.Checkbutton(
                mainframe,
                variable=self._tgt_family[current_row - 13]["Check"],
                onvalue="yes",
                offvalue="no",
            ).grid(column=2, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._tgt_family[current_row - 13]["Given"]
            ).grid(column=3, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._tgt_family[current_row - 13]["Surname"]
            ).grid(column=4, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._tgt_family[current_row - 13]["BirthYear"]
            ).grid(column=5, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._tgt_family[current_row - 13]["DeathYear"]
            ).grid(column=6, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._tgt_family[current_row - 13]["ID"]
            ).grid(column=7, row=current_row, sticky=EW)

        for current_row in range(11, 37):
            ttk.Label(
                mainframe, textvariable=self._ppl[current_row - 11]["Given"]
            ).grid(column=11, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._ppl[current_row - 11]["Surname"]
            ).grid(column=12, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._ppl[current_row - 11]["BirthYear"]
            ).grid(column=13, row=current_row, sticky=EW)
            ttk.Label(
                mainframe, textvariable=self._ppl[current_row - 11]["DeathYear"]
            ).grid(column=14, row=current_row, sticky=EW)
            ttk.Label(mainframe, textvariable=self._ppl[current_row - 11]["ID"]).grid(
                column=15, row=current_row, sticky=EW
            )

        current_row = 14
        ttk.Label(mainframe, text="Father").grid(column=1, row=current_row, sticky=EW)

        current_row = 15
        ttk.Label(mainframe, text="Mother").grid(column=1, row=current_row, sticky=EW)

        current_row = 16
        ttk.Label(mainframe, text="Spouses").grid(column=1, row=current_row, sticky=EW)

        current_row = 20
        ttk.Label(mainframe, text="Children").grid(column=1, row=current_row, sticky=EW)

        current_row = 35
        titleSep3 = ttk.Separator(mainframe, orient=HORIZONTAL)
        titleSep3.grid(column=0, row=current_row, columnspan="8", sticky="we")

        current_row = 36
        ttk.Label(mainframe, text="Type of file to add:").grid(
            column=3, row=current_row, columnspan="3", sticky=EW
        )

        current_row = 37
        ttk.Button(
            mainframe, text="Image\nReference", command=self._on_setup_image_ref
        ).grid(column=3, row=current_row, sticky=W, columnspan=1, rowspan=1)
        ttk.Button(
            mainframe, text="Inline\nText", command=self._on_setup_build_inline_txt
        ).grid(column=4, row=current_row, sticky=W, columnspan=1, rowspan=1)
        ttk.Button(
            mainframe, text="External\nhtml", command=self._on_setup_build_ext_html
        ).grid(column=5, row=current_row, sticky=W, columnspan=1, rowspan=1)
        ttk.Button(
            mainframe, text="Generate\nFile", command=self._on_generate_file
        ).grid(column=10, row=current_row, sticky=W, columnspan=1, rowspan=1)

        current_row = 38

        for child in mainframe.winfo_children():
            child.grid_configure(padx=2, pady=2)

    def mainloop(self):
        self._root.mainloop()

    def _populate_match_label(self):
        numPeoplePopulated = min(self._MAX_MATCHES_VISIBLE, len(self._matched_persons))
        for number in range(numPeoplePopulated):
            namestring = rmagic.build_given_name(self._matched_persons[number]["Given"])
            self._match[number]["Given"].set(str(namestring))
            self._match[number]["Surname"].set(
                str(self._matched_persons[number]["Surname"])
            )
            self._match[number]["BirthYear"].set(
                str(self._matched_persons[number]["BirthYear"])
            )
        for number in range(numPeoplePopulated, self._MAX_MATCHES_VISIBLE):
            self._match[number]["Given"].set("-")
            self._match[number]["Surname"].set("-")
            self._match[number]["BirthYear"].set("-")

    def _populate_target_relation(self, target, person):
        namestring = rmagic.build_given_name(person["Given"])
        target["Given"].set(str(namestring))
        target["Surname"].set(str(person["Surname"]))

        # If there is no BirthYear, RootsMagic returns '0" I want to set the
        # BirthYear to '0000' if there is no BirthYear - chg: 20141122 rkp
        birth_year = str(person["BirthYear"])
        if birth_year == "0":
            target["BirthYear"].set("0000")
        else:
            target["BirthYear"].set(birth_year)

        death_year = str(person["DeathYear"])
        if death_year == "0":
            target["DeathYear"].set("")
        else:
            target["DeathYear"].set(death_year)
        target["ID"].set(str(person["OwnerID"]))

    def _on_search_for_matches(self, *args):
        given_name_value = str(self._srch_person["Given"].get())
        surname_value = str(self._srch_person["Surname"].get())
        birthyear_value = str(self._srch_person["BirthYear"].get())

        name_dict = {
            "Surname": surname_value,
            "Given": given_name_value,
            "BirthYear": birthyear_value,
        }

        self._matched_persons = rmagic.fetch_person_from_fuzzy_name(
            self._tables["NameTable"], name_dict
        )
        self._populate_match_label()

    def _on_view_possible_person(self, *args):
        # identify the target person
        person_no = int(self._selected_person.get())

        # Clear the possible person table
        for person in range(self._MAX_TARGET_FAMILIES_VISIBLE):
            for category in self._tgt_family[person]:
                self._tgt_family[person][category].set("-")

        target = 0
        self._populate_target_relation(
            self._tgt_family[target], self._matched_persons[person_no]
        )

        parents = rmagic.fetch_parents_from_id(
            self._tables["PersonTable"],
            self._tables["NameTable"],
            self._tables["FamilyTable"],
            self._matched_persons[person_no]["OwnerID"],
        )
        print(
            "self._matched_persons[person_no] = ",
            self._matched_persons[person_no],
            "    parents = ",
            parents,
        )

        father = 1
        self._populate_target_relation(self._tgt_family[father], parents["Father"])

        mother = 2
        self._populate_target_relation(self._tgt_family[mother], parents["Mother"])

        spouses = rmagic.fetch_spouses_from_id(
            self._tables["NameTable"],
            self._tables["PersonTable"],
            self._tables["FamilyTable"],
            self._matched_persons[person_no]["OwnerID"],
        )

        for spouse_no in range(len(spouses)):
            fam_spouses = 3
            self._populate_target_relation(
                self._tgt_family[fam_spouses + spouse_no], spouses[spouse_no]
            )

        children = rmagic.fetch_children_from_id(
            self._tables["ChildTable"],
            self._tables["NameTable"],
            self._tables["PersonTable"],
            self._tables["FamilyTable"],
            self._matched_persons[person_no]["OwnerID"],
        )

        for child_no in range(len(children)):
            fam_children = 7
            self._populate_target_relation(
                self._tgt_family[fam_children + child_no], children[child_no]
            )

    def _on_add_to_people_ref(self, *args):
        # How many people are already in the People Referenced table (ppl_ref_no)
        ppl_ref_no = 0
        for i in range(self._MAX_PEOPLE_REFERENCED):
            if self._ppl[ppl_ref_no]["Given"].get() != "-":
                ppl_ref_no += 1
        # Append checked people to the People Referenced table
        for tf_no in range(self._MAX_TARGET_FAMILIES_VISIBLE):
            if self._tgt_family[tf_no]["Check"].get() == "yes":
                self._ppl[ppl_ref_no]["Given"].set(
                    self._tgt_family[tf_no]["Given"].get()
                )
                self._ppl[ppl_ref_no]["Surname"].set(
                    self._tgt_family[tf_no]["Surname"].get()
                )
                self._ppl[ppl_ref_no]["BirthYear"].set(
                    self._tgt_family[tf_no]["BirthYear"].get()
                )
                death_year = self._tgt_family[tf_no]["DeathYear"].get()
                if death_year == "0":
                    death_year = ""
                self._ppl[ppl_ref_no]["DeathYear"].set(death_year)
                self._ppl[ppl_ref_no]["ID"].set(self._tgt_family[tf_no]["ID"].get())
                ppl_ref_no += 1

    def _on_setup_image_ref(self, *args):
        # Set the file generation labels
        self._file_gen["Header"].set("Image Reference")
        self._file_gen["Artifact_ID_Label"].set("ID	YYYYMMDD##")
        self._file_gen["Artifact_Title_Label"].set("Title")
        self._file_gen["Artifact_Caption_Label"].set("Caption")
        self._file_gen["Artifact_Misc_Label"].set("Comment")
        self._file_gen["Artifact_Path_Label"].set("Path")

        # Only display the people who have been selected
        ppl_ref = 0
        for ref in range(len(self._tgt_family)):
            if str(self._tgt_family[ref]["Check"].get()) == "yes":
                self._ppl[ppl_ref]["Given"].set(
                    str(self._tgt_family[ref]["Given"].get())
                )
                self._ppl[ppl_ref]["Surname"].set(
                    str(self._tgt_family[ref]["Surname"].get())
                )
                self._ppl[ppl_ref]["BirthYear"].set(
                    str(self._tgt_family[ref]["BirthYear"].get())
                )
                self._ppl[ppl_ref]["DeathYear"].set(
                    str(self._tgt_family[ref]["DeathYear"].get())
                )
                self._ppl[ppl_ref]["ID"].set(str(self._tgt_family[ref]["ID"].get()))
                ppl_ref += 1
        for ppl_ref in range(ppl_ref, len(self._tgt_family)):
            self._ppl[ppl_ref]["Given"].set("-")
            self._ppl[ppl_ref]["Surname"].set("-")
            self._ppl[ppl_ref]["BirthYear"].set("-")
            self._ppl[ppl_ref]["DeathYear"].set("-")
            self._ppl[ppl_ref]["ID"].set("-")

    def _on_setup_build_ext_html(self, *args):
        # Set the file generation labels
        self._file_gen["Header"].set("External HTML")
        self._file_gen["Artifact_ID_Label"].set("ID	YYYYMMDD##")
        self._file_gen["Artifact_Title_Label"].set("Title")
        self._file_gen["Artifact_Caption_Label"].set("File")
        self._file_gen["Artifact_Misc_Label"].set("Folder")
        self._file_gen["Artifact_Path_Label"].set("Path")

        # Only display the people who have been selected
        ppl_ref = 0
        for ref in range(len(self._tgt_family)):
            if str(self._tgt_family[ref]["Check"].get()) == "yes":
                self._ppl[ppl_ref]["Given"].set(
                    str(self._tgt_family[ref]["Given"].get())
                )
                self._ppl[ppl_ref]["Surname"].set(
                    str(self._tgt_family[ref]["Surname"].get())
                )
                self._ppl[ppl_ref]["BirthYear"].set(
                    str(self._tgt_family[ref]["BirthYear"].get())
                )
                self._ppl[ppl_ref]["DeathYear"].set(
                    str(self._tgt_family[ref]["DeathYear"].get())
                )
                self._ppl[ppl_ref]["ID"].set(str(self._tgt_family[ref]["ID"].get()))
                ppl_ref += 1
        for ppl_ref in range(ppl_ref, len(self._tgt_family)):
            self._ppl[ppl_ref]["Given"].set("-")
            self._ppl[ppl_ref]["Surname"].set("-")
            self._ppl[ppl_ref]["BirthYear"].set("-")
            self._ppl[ppl_ref]["DeathYear"].set("-")
            self._ppl[ppl_ref]["ID"].set("-")

    def _on_setup_build_inline_txt(self, *args):
        # Set the file generation labels
        self._file_gen["Header"].set("Inline Text")
        self._file_gen["Artifact_ID_Label"].set("ID	YYYYMMDD##")
        self._file_gen["Artifact_Title_Label"].set("Title")
        self._file_gen["Artifact_Caption_Label"].set("")
        self._file_gen["Artifact_Misc_Label"].set("")
        self._file_gen["Artifact_Path_Label"].set("Path")

        # Only display the people who have been selected
        ppl_ref = 0
        for ref in range(len(self._tgt_family)):
            if str(self._tgt_family[ref]["Check"].get()) == "yes":
                self._ppl[ppl_ref]["Given"].set(
                    str(self._tgt_family[ref]["Given"].get())
                )
                self._ppl[ppl_ref]["Surname"].set(
                    str(self._tgt_family[ref]["Surname"].get())
                )
                self._ppl[ppl_ref]["BirthYear"].set(
                    str(self._tgt_family[ref]["BirthYear"].get())
                )
                self._ppl[ppl_ref]["DeathYear"].set(
                    str(self._tgt_family[ref]["DeathYear"].get())
                )
                self._ppl[ppl_ref]["ID"].set(str(self._tgt_family[ref]["ID"].get()))
                ppl_ref += 1
        for ppl_ref in range(ppl_ref, len(self._tgt_family)):
            self._ppl[ppl_ref]["Given"].set("-")
            self._ppl[ppl_ref]["Surname"].set("-")
            self._ppl[ppl_ref]["BirthYear"].set("-")
            self._ppl[ppl_ref]["DeathYear"].set("-")
            self._ppl[ppl_ref]["ID"].set("-")

    def _on_generate_file(self, *args):
        artifact_ID = self._file_gen["Artifact_ID"].get()
        # I need to make this also work for the case where the path separator is '/'
        artifact_path = self._file_gen["Artifact_Path"].get().replace("\\", "/")
        artifact_label = artifact_path.rpartition("/")[2]
        artifact_label = artifact_label  # delete this line !!!!
        file_name = artifact_path + "/" + artifact_ID + artifact_label + ".xml"
        parent_path = os.path.split(artifact_path)

        referenced_people = ""
        for person_no in range(self._MAX_PEOPLE_REFERENCED):
            if self._ppl[person_no]["Surname"].get() != "-":
                referenced_person = (
                    self._ppl[person_no]["Surname"].get()
                    + self._ppl[person_no]["Given"].get().replace(" ", "")
                    + self._ppl[person_no]["BirthYear"].get()
                )
                fully_referenced_person = referenced_person + self._get_mother_genwebid(
                    referenced_person
                )
                referenced_people = fully_referenced_person + ";" + referenced_people
        referenced_people = referenced_people.rstrip(";")

        date_modified = str(datetime.date.today())
        # the following 5 lines will save the date of the latest change to an xml file
        # I will use this to avoid re-creating the xml dictionary files if nothing has changed
        head_path = os.path.split(artifact_path)
        file_name_latest_xml_mod = (
            head_path[0] + "/___dictionaries/file_name_latest_xml_mod.dat"
        )
        with open(file_name_latest_xml_mod, "w") as g:
            g.write(date_modified)
            g.close()

        if os.path.isfile(file_name) == True:
            file_name = artifact_path + "/" + artifact_ID + artifact_label + "_new.xml"
            print(
                "Need to resolve differences between the file ",
                file_name,
                " and its previous version",
            )

        try:
            with open(file_name, "w") as f:
                f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
                if self._file_gen["Header"].get() == "Inline Text":
                    f.write("<inline>\n")
                    f.write("\t<path>" + artifact_label + "</path>\n")
                    f.write("\t<file>" + artifact_ID + artifact_label + ".src</file>\n")
                    f.write(
                        "\t<title>"
                        + self._file_gen["Artifact_Title"].get()
                        + "</title>\n"
                    )
                    f.write(
                        "\t<comment>"
                        + self._file_gen["Artifact_Misc"].get()
                        + "</comment>\n"
                    )
                    f.write("\t<people>" + referenced_people + "</people>\n")
                    f.write("\t<mod_date>" + date_modified + "</mod_date>\n")
                    f.write("</inline>")

                elif self._file_gen["Header"].get() == "External HTML":
                    f.write("<href>\n")
                    f.write("\t<path>" + artifact_label + "</path>\n")
                    f.write(
                        "\t<file>"
                        + self._file_gen["Artifact_Caption"].get()
                        + "</file>\n"
                    )
                    f.write(
                        "\t<folder>"
                        + self._file_gen["Artifact_Misc"].get()
                        + "</folder>\n"
                    )
                    f.write(
                        "\t<title>"
                        + self._file_gen["Artifact_Title"].get()
                        + "</title>\n"
                    )
                    f.write("\t<people>" + referenced_people + "</people>\n")
                    f.write("\t<mod_date>" + date_modified + "</mod_date>\n")
                    f.write("</href>")

                elif self._file_gen["Header"].get() == "Image Reference":
                    f.write("<picture>\n")
                    f.write("\t<path>" + artifact_label + "</path>\n")
                    f.write("\t<file>" + artifact_ID + artifact_label + ".jpg</file>\n")
                    f.write(
                        "\t<title>"
                        + self._file_gen["Artifact_Title"].get()
                        + "</title>\n"
                    )
                    f.write(
                        "\t<caption>"
                        + self._file_gen["Artifact_Caption"].get()
                        + "</caption>\n"
                    )
                    f.write(
                        "\t<comment>"
                        + self._file_gen["Artifact_Misc"].get()
                        + "</comment>\n"
                    )
                    f.write("\t<people>" + referenced_people + "</people>\n")
                    f.write("\t<height>" + "" + "</height>\n")
                    f.write("\t<mod_date>" + date_modified + "</mod_date>\n")
                    f.write("</picture>")

        except IOError:
            print("Failed to open ", file_name)

        # Reset the referenced people
        for ppl_no in range(self._MAX_PEOPLE_REFERENCED):
            self._ppl[ppl_no]["Given"].set("-")
            self._ppl[ppl_no]["Surname"].set("-")
            self._ppl[ppl_no]["BirthYear"].set("-")
            self._ppl[ppl_no]["DeathYear"].set("-")
            self._ppl[ppl_no]["ID"].set("-")

    def _separate_names(self, item):
        """given a string that is a concatenation of names with their first
        letters capitalized [e.g. PageRobertK1949], separate them into
        separate words or characters and the date -
        assumes person IDs contain no spaces and every person's ID has
        a date or 0000
        The results are a dictionary with the following keys
        'BirthYear'
        'Surname'
        'Given'
        'Initial'"""

        # extract the date
        debug = "no"
        if item == "":
            debug = "yes"
        person = {}
        person["BirthYear"] = item.strip(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'"
        )
        item = item.strip("0123456789")

        people_re = re.compile(r"([A-Z][a-z]+)")

        names = people_re.split(item)
        names = [x for x in names if x != ""]

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

        person["FullName"] = person["Given"] + person["Initial"] + person["Surname"]

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

    def _get_mother_genwebid(self, target_genwebid):
        debug = "False"
        proper_format = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]")
        folders_path = "C:/Family_History/FamilyHistoryWeb/Individual_Web_Pages"
        target_genwebid = target_genwebid.replace(" ", "")
        if not proper_format.match(target_genwebid):
            print(
                "folders_path = ",
                folders_path,
                "   target_genwebid = ",
                target_genwebid,
            )
            chg_to_long_id_file = open(
                folders_path + "/zzz_xml_file_name_issue.txt", "a"
            )
            chg_to_long_id_file.write(
                "Improper format for target genwebid " + target_genwebid + "\n"
            )
            chg_to_long_id_file.close()
            return ""
        else:
            person_id_dict = self._separate_names(target_genwebid)
            person_matches = rmagic.fetch_person_from_name(
                self._tables["NameTable"], self._tables["PersonTable"], person_id_dict
            )
            if len(person_matches) == 0:
                chg_to_long_id_file = open(
                    folders_path + "/zzz_xml_file_name_issue.txt", "a"
                )
                chg_to_long_id_file.write(
                    "_get_mother_genwebid - Could not find rmagic match for person with target_genwebid = "
                    + target_genwebid
                    + "\n"
                )
                chg_to_long_id_file.close()
                return ""
            elif len(person_matches) > 1:
                chg_to_long_id_file = open(
                    folders_path + "/zzz_xml_file_name_issue.txt", "a"
                )
                chg_to_long_id_file.write(
                    "_get_mother_genwebid - Multiple matches for rmagic person with target_genwebid = "
                    + target_genwebid
                    + "\n"
                )
                for match_person in person_matches:
                    chg_to_long_id_file.write(
                        "Multiple matches for rmagic person. Match = "
                        + match_person["GenWebID"]
                        + "\n"
                    )
                chg_to_long_id_file.close()
                return ""
            parents = rmagic.fetch_parents_from_id(
                self._tables["PersonTable"],
                self._tables["NameTable"],
                self._tables["FamilyTable"],
                person_matches[0]["OwnerID"],
            )

            if debug == True and target_genwebid == "":
                print("_get_mother_genwebid - target_genwebid = ", target_genwebid)
                print("parents['Mother']['GenWebID'] = ", parents["Mother"]["GenWebID"])
                print("parents['Mother']['Surname'] = ", parents["Mother"]["Surname"])
                print("parents['Mother']['Given'][0] = ", parents["Mother"]["Given"][0])
            if (
                parents["Mother"]["GenWebID"] == ""
                or len(parents["Mother"]["Surname"]) == 0
                or len(parents["Mother"]["Given"][0]) == 0
            ):
                mother_genwebid = "-"
            else:
                mother_genwebid = parents["Mother"]["GenWebID"]

        return mother_genwebid


def main():
    # Get the RootsMagic database info
    rmagicPath = sys.argv[1]
    editor = Editor(rmagicPath)
    editor.mainloop()


if __name__ == "__main__":
    main()
