##
# j2static generator
# Copyright (c) 2018, Joseph Walton-Rivers
##

import jinja2

import os
import tempfile
import subprocess
import shutil
import pathlib

class BaseGenerator(object):
    """ """

    def __init__(self, template_dir='.'):
        self.jinja = self._mkenv(template_dir)

    def render(self, path, context=dict()):
        """Build a single page and return the result"""
        template = self.get_file(path)
        return template.render(context)

    def generate(self, path, outfile, context=dict()):
        """ """
        # ensure directory exists...
        out_dir = outfile.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        with open(outfile, 'w') as fp:
            fp.write(self.render(path, context=context))

    def filter(self, filename):
        filepath = pathlib.Path(filename)

        # if the filename starts with '_' we treat it as abstract
        if filepath.name[0] == '_':
           return False
        return self.is_template(filepath)

    def is_template(self, filepath):
        return True

    def get_files(self):
        """ """
        return self.jinja.list_templates(filter_func=self.filter)

    def get_file(self, name):
        return self.jinja.get_template(name)

class Website(BaseGenerator):
    """ """

    def is_template(self, filepath):
        return filepath.suffix in (".html", ".xhtml", ".xml")

    def _mkenv(self, template_dir):
        """Make a jinja enviroment object suitable for a website"""
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=True
        )

class PlainText(BaseGenerator):
    """ """

    def _get_extentions(self):
        return ("txt",)

    def _mkenv(self, template_dir):
        """Make a jinja enviroment object suitable for plain text processing"""
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=False
        )

class Latex(BaseGenerator):
    """ """

    def _get_extentions(self):
        return ("tex",)

    def _mkenv(self, template_dir):
        """Make a jinja enviroment object suitable for plain text processing"""
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            block_start_string = '\BLOCK{',
            block_end_string = '}',
            variable_start_string = '\VAR{',
            variable_end_string = '}',
            comment_start_string = '\#{',
            comment_end_string = '}',
            line_statement_prefix = '%%',
            line_comment_prefix = '%#',
            trim_blocks = True,
            autoescape = False
        )

class TexPDF(BaseGenerator):
    """Use latexmk and a tempdir to make PDFs"""

    def __init__(self, template_dir='.'):
       self.texgen = Latex(template_dir=template_dir)

    def _get_extentions(self):
        return self.texgen._get_extentions()

    def generate(self, path, outfile, context=None):
        # ensure directory exists...
        out_dir = outfile.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as td:
            tmp_path = pathlib.Path(td)
            self.texgen.generate(path, tmp_path / 'test.tex', context=context)
            subprocess.run( ['latexmk', '-pdf', '-interaction=nonstopmode', 'test.tex'], cwd=td )
            shutil.copy(os.path.join(td, 'test.pdf'), outfile)

    def get_file(self, path):
        """ """
        return self.texgen.get_file(path)


_types = {
    "html": Website,
    "txt": PlainText,
    "tex": Latex,
    "pdf": TexPDF
}

def get_builder(build_type, template_dir):
    return _types[build_type](template_dir)
