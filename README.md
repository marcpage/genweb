![status sheild](https://img.shields.io/static/v1?label=status&message=starting...&color=inactive&style=plastic)
![GitHub](https://img.shields.io/github/license/marcpage/genweb?style=plastic)
[![commit sheild](https://img.shields.io/github/last-commit/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb/commits)
[![activity sheild](https://img.shields.io/github/commit-activity/m/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb/commits)
![GitHub top language](https://img.shields.io/github/languages/top/marcpage/genweb?style=plastic)
[![size sheild](https://img.shields.io/github/languages/code-size/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb)
[![issues sheild](https://img.shields.io/github/issues-raw/marcpage/genweb?style=plastic)](https://github.com/marcpage/genweb/issues)
[![follow sheild](https://img.shields.io/github/followers/marcpage?label=Follow&style=social)](https://github.com/marcpage?tab=followers)
[![watch sheild](https://img.shields.io/github/watchers/marcpage/genweb?label=Watch&style=social)](https://github.com/marcpage/genweb/watchers)

# genweb
Generate a family history website



# Format source

On Linux:

- `./pr_build.py format`

or

- `python3 pr_build.py format`



# Validate source

On Linux:

- `./pr_build.py`

or

- `python3 pr_build.py`



# Setup

1. `python3 -m venv .venv`
1. Linux: `source .venv/bin/activate`
1. `pip3 install -r requirements.txt`



# Usage

`pytest`

`python3 -m genweb.artifact_editor <path to roots magic db>`

`python3 -m genweb.build_web_pages <path to roots magic db> <web folder path> <admin email>`



# Helpful git commands

- **git pull** - Get latest changes from GitHub
- **git status** - Check for local changes
- **git add [file]** - Add a new file to local database
- **git mv [src] [dst]** - Move or rename local file
- **git rm [file]** - Delete file
- **git commit -a** - Put current changes into local database
- **git push** - Push changes in local database to GitHub
- **git checkout -b users/pagerk/[branch name]** - Creat local branch
