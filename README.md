# genweb

![status sheild](https://img.shields.io/static/v1?label=status&message=starting...&color=blue&style=plastic)
[![status sheild](https://img.shields.io/static/v1?label=released&message=none&color=active&style=plastic)](https://pypi.org/project/devopsdriver/0.1.45/)
[![GitHub](https://img.shields.io/github/license/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb?tab=Unlicense-1-ov-file#readme)
[![GitHub contributors](https://img.shields.io/github/contributors/marcpage/genweb?style=flat)](https://github.com/marcpage/genweb/graphs/contributors)
[![PR's Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)

[![commit sheild](https://img.shields.io/github/last-commit/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb/commits)
[![activity sheild](https://img.shields.io/github/commit-activity/m/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb/commits)
[![GitHub top language](https://img.shields.io/github/languages/top/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb)
[![size sheild](https://img.shields.io/github/languages/code-size/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb)

[![example workflow](https://github.com/marcpage/genweb/actions/workflows/CI.yml/badge.svg)](https://github.com/marcpage/genweb/actions/workflows/CI.yml)
[![status sheild](https://img.shields.io/static/v1?label=test+coverage&message=65%&color=active&style=plastic)](https://github.com/marcpage/genweb/blob/main/Makefile#L4)
[![issues sheild](https://img.shields.io/github/issues-raw/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/marcpage/genweb?style=flat)](https://github.com/marcpage/genweb/pulls)

[![follow sheild](https://img.shields.io/github/followers/marcpage?label=Follow&style=social)](https://github.com/marcpage?tab=followers)
[![watch sheild](https://img.shields.io/github/watchers/marcpage/genweb?label=Watch&style=social)](https://github.com/marcpage/genweb/watchers)

[![Python](https://img.shields.io/static/v1?label=&message=Pure%20Python&color=ffde57&style=plastic&logo=python)](https://python.org/)


## Description

Genweb is a tool that you can use to construct a website with your pictures in conjucntion with a geneology source (GEDCOM file).

## Concepts

When getting started there are a few pieces to put things together:
- **A GEDCOM file** this file can be exported from most geneology software
- **Collection of Artifacts** This is a folder that contains pictures, movies, and other files of interest
- **metadata.yml** This file describes the Artifacts and connects them with people (**TODO**: create a tool to edit this file)
- **TODO**: *(optional)* An AWS S3 and remote web server to share the site publicly and serve as a source-of-truth for maintainers of the site


## How to use

1. Export a GEDCOM file from you geneology software (tested with RootsMagic)
2. Collect all your artifacts into a folder
  - These can be images, movides, and even mini-websites
3. Create `metadata.yml` in your artifacts folder
  - This will describe the files and link people to them
4. *(optional)* Create `aliases.yml` in your artifacts folder
  - People identifiers are generated by person name, birthyear, mother's name, mother's birthyear
  - As family history research is conducted, the calculated identifiers can change
  - This file maps old names to new names
5. Create file `genweb.yml`
6. Run `python3 -m genweb.genweb`

## genweb.yml

`genweb.yml` should be created at the following location:

- **Windows**: ???
- **Linux**: `~/.devopsdriver/genweb.yml`
- **macOS**: `~/Library/Preferences/genweb.yml`

It should contain the following contents:

```yaml
binaries_dir: path/to/artifacts/
metadata_yaml: /path/to/file.yml
gedcom_path: /path/to/file.ged
site_dir: path/to/output/
alias_path: /path/to/file.yml
```

## %binaries_dir%

The `binaries_dir` is the directory that all your photos, videos, sub-websites reside.

**Note**: All pictures in this directory that are not part of a sub-website should have a filename unique in the directory (including all subdirectories). 
This is usually accomplished by naming them `YYYYMMDDNNperson_identifier.ext`.
Where `YYYY` is the four-digit year, `MM` is the two-digit month, `DD` is the two-digit day, `NN` is a two-digit index, and `ext` is the file extension (like `.jpg`).


## %metadata_yaml%

### %metadata_yaml% editor

There is an editor in the works, but does not currently work yet.
To run the editor:

1. Add `webserver.yml` next to `genweb.yml`
2. Execute `python3 -m genweb.webserver`
3. Point your browser at [localhost:8000](http://localhost:8000)

Here are the current features of the non-functional editor:

- The metadata type selector should change the appropriate fields shown in the editor for the chosen type
- Clicking the 🔎 button next to the `Identifier` field will allow you to search and load existing metadata
- If the `Identifier` field is an existing metadata identifier, the submit button changes from `Add` to `Update`
- Clicking the 🔎 button next to the `People` field will reveal a people search
- Typing in the people search will filter the people ids
- Clicking on a person in the filter list will display the person and their family
- This will allow copy/pasting of people ids into the `People` field

#### webserver.yml

```yaml
gedcom_path: /path/to/file.ged
metadata_yaml: /path/to/file.yml
alias_path: /path/to/file.yml
```

### %metadata_yaml% format
The format for the `metadata.yml` file is (**Note**: All artifact identifiers should start with the year):

```yaml
year_picture_artifact_identifier:
    type: picture
    title: Title of the picture
    file: picture_artifact_identifier.jpg
    path: owning_person_identifier
    width: 500  # or height: 500
    people:
        - person_identifier
        - owning_person_identifier
year_inline_artifact_identifier:
  type: inline
  title: Title of the inline code
  path: owning_person_identifier
  contents: '<b>html</b> contents to insert into the page'
  mod_date: '2015-05-26'
  people:
  - owning_person_identifier
  - person_identifier
year_href_artifact_identifier:
  type: href
  title: Title of the sub-webpage
  path: owning_person_identifier
  folder: folder_name  # %artifacts_dir%/owning_person_identifier/folder_name
  file: start_page.html  # %artifacts_dir%/owning_person_identifier/folder_name/start_page.html
  mod_date: '2015-05-18'
  people:
  - owning_person_identifier
  - person_identifier
```


## %gedcom_path%

This is the path to a GEDCOM 5.5 file. 
The GEDCOM export from [RootsMagic](https://www.rootsmagic.com) has been tested and works.
This file is used to generate the relationships and define person-identifiers.

### Person-identifiers

Person-identifiers are of the format `LastFirstIYYYYLastFirstIYYYY` or `LastFirstIYYYY-`.
It consists of the last name, first name, middle initial (first middle name), and year of birth.
If the mother is known, the identifier has the person followed by the mother's name.
If the mother is not known, a hypher (-) suffix is used.

## %site_dir%

This is the directory that the website will be generated into.
This directory needs to be on the same disk (technically filesystem) as `%binaries_dir%`.
Instead of copying files from `%binaries_dir%` to `%site_dir%` they are linked, saving time and disk space.

## %alias_path%

Family information gets updated all the time.
For instance if someone's mother is discovered, the person-identifier for them may chance from `JonesThomasI2004-` to `JonesThomasI2004SmithSallyT1975`.
Since all the information in `%metadata_yaml%` is based on person-identifiers, you can account for changes like this without having to edit everything by using this file.
It will take the new person-identifier from the GEDCOM updates and translate them into the old identifier.

The format of the file is:
```yaml
oldest_person_id:
    - old_person_id
    - newest_person_id

oldest_person_id:
    - newest_person_id
```
