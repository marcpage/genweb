#!/usr/bin/env python3

"""
    Generate web pages
"""

import os

import mako.lookup


def save_alpha_toc(path, list_of_people):
    write(path, "alpha_toc.html.mako", people=list_of_people)


def save_personal(family_dict, persons_xml_dict, admin_email, folders_path):
    path = os.path.join(folders_path, family_dict["target"]["long_genwebid"])
    os.makedirs(path, exist_ok=True)
    write(
        os.path.join(path, "index.html"),
        "person_index.html.mako",
        family_dict=family_dict,
        persons_xml_dict=persons_xml_dict,
        admin_email=admin_email,
        folders_path=folders_path,
    )


def write(path, template, **kwargs):
    with open(path, "w", encoding="utf-8") as html_file:
        html_file.write(render(os.path.join("templates", template), **kwargs))


def render(template_path, *search_dirs, **args):
    """Render a template file searching for includes in given directories and using given args"""
    script_dir = os.path.split(os.path.realpath(__file__))[0]
    search_dirs = list(search_dirs)
    script_parent_dir = os.path.split(script_dir)[0]
    search_dirs.extend(
        [
            os.path.join(script_parent_dir, x)
            for x in os.listdir(script_parent_dir)
            if os.path.isdir(os.path.join(script_parent_dir, x))
        ]
    )
    search_dirs.extend(
        [
            os.path.join(script_dir, x)
            for x in os.listdir(script_dir)
            if os.path.isdir(os.path.join(script_dir, x))
        ]
    )
    search_dirs.append(script_parent_dir)
    search_dirs.append(os.path.split(template_path)[0])
    lookup = mako.lookup.TemplateLookup(
        directories=list(set(search_dirs)),
        module_directory="/tmp/mako_modules",
    )
    template = lookup.get_template(os.path.split(template_path)[1])

    return template.render(**args)
