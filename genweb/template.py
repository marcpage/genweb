#!/usr/bin/env python3


""" Render a .mako template """

from os.path import realpath, dirname, basename, join, isdir
from os import listdir

from mako.lookup import TemplateLookup


CACHE_DIR = "/tmp/mako_modules"


def render(template_path: str, *search_dirs, **args) -> str:
    """Render a template file searching for includes in given directories and using given args

    Args:
        template_path (str): The path to the template file
        search_dirs (str*): Directories to search for includes
        args (dict[str:any]): Args to pass to the script

    Returns:
        _type_: _description_
    """
    script_dir = dirname(realpath(__file__))
    search_dirs = list(search_dirs)
    script_parent_dir = dirname(script_dir)
    search_dirs.extend(
        [
            join(script_parent_dir, x)
            for x in listdir(script_parent_dir)
            if isdir(join(script_parent_dir, x))
        ]
    )
    search_dirs.extend(
        [join(script_dir, x) for x in listdir(script_dir) if isdir(join(script_dir, x))]
    )
    search_dirs.append(script_parent_dir)
    search_dirs.append(dirname(template_path))
    lookup = TemplateLookup(
        directories=list(set(search_dirs)), module_directory=CACHE_DIR
    )
    template = lookup.get_template(basename(template_path))
    return template.render(**args)


def render_to_file(output_path: str, template_path: str, *search_dirs, **args) -> None:
    """Render a template to a file on disk

    Args:
        output_path (str): The file to render into
        template_path (str): The template to render
        search_dirs (*str): Any directories to search for includes
        args (**dict[str:any]): Arguments to pass to the template
    """
    contents = render(template_path, *search_dirs, **args)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(contents)
