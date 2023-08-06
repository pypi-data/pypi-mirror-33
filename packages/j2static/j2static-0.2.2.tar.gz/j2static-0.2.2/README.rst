J2static
========

About this project
------------------
This project aims to unify a set of internally produced scripts for generating
static content, choosing to standardise on the jinja2 templating engine.

Simply put, this project aims to provide utilities to do the following:

* Static site generation (for gitlab)
* Generate customised summary documents based on submissions
* Generate PDFs from CSV files and templates (mail merges)

Development
-----------
The recommended way to develop the tools in the package is to use development
mode of setup.py, this will create executables in your path which can be used
to test changes.

::

  ./setup.py develop --user

We're open to pull requests and feature requests, this should be done via our
gitlab_ server.

Usage
-----
The project consits of two executables, j2static, the static site generator
and j2merge, the mail merge tool.

j2static executable
...................
j2static builds files stored in a directory named _templates/ using jinja2,
generating output documents in site/. The tool will ignore any file that starts
with an underscore, allowing for the creation of templates.

j2static can also act as a webserver for local testing. In this mode the server
will not generate output documents on disk, but will instead generate and send 
them to the browser 'on the fly'. This is useful if you have javascript on
your site and don't want to fall foul of the browser's security settings when
testing with local files.

::

  j2static build # use templates in the _templates/ directory to build the site
  j2static serve # start a webserver on localhost (for development)


j2merge executable
..................
j2merge is a 'mail merge' tool for combining csv files with a template document
this is useful for producing reports or personalised documents. This can be
optionally combined with a LaTeX distrubtion to generate PDFs.

j2merge assumes that the csv file provided has headers and contains a row named
id which will be used for the resulting filenames. The data for each row will
be available in the template as the variable row.

::

  j2merge data.csv # combine data.csv and base.html to generate documents
  j2merge data.csv -out pdf # combine data.csv and base.tex to generate pdfs

.. _gitlab: https://git.fossgalaxy.com
