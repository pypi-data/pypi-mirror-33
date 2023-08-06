#! /usr/bin/env python3

import pathlib
import shutil
import jinja2

from j2static import build
from j2static.tools.merge import load_data

def find_all(dirpath):
    files = []
    for path in dirpath.iterdir():
        if path.is_file():
            files.append(path)
        else:
            files.extend( find_all(path) )
    return files

def generate(args):
    out_path = pathlib.Path(args.out_dir)
    data_path = pathlib.Path(args.data_dir)
    template_path = pathlib.Path(args.template_dir)

    if not template_path.exists():
        print("could not find template path, are you in the right place?")
        return

    generator = build.get_builder("html", args.template_dir)

    for path in find_all(template_path):
        relative_path = path.relative_to(template_path)
        out_file = out_path / relative_path

        if generator.filter(path):
            context = []

            data_file = data_path / (relative_path.stem + ".json")
            if data_file.exists():
                context = load_data(data_file)

            try:
                generator.generate(str(relative_path), out_file, context=context)
            except jinja2.TemplateSyntaxError as e:
                print( "Build Error: {e.name}, line: {e.lineno} - {e.message}".format(e=e) )
        elif path.is_file() and relative_path.name[0] != '_':
            out_file.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(path, out_file)
