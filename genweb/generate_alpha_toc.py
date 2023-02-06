#!/usr/bin/env python3


import os

import mako.lookup

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


def save(path, people):
    with open(path, 'w', encoding='utf-8') as html_file:
        html_file.write(render('alpha_toc.html.mako', people=people))
