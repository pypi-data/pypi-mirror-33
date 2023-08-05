"""
``Pdfposter`` can be used to create a large poster by building it from
multiple pages and/or printing it on large media. It expects as input a
PDF file, normally printing on a single page. The output is again a
PDF file, maybe containing multiple pages together building the
poster.
The input page will be scaled to obtain the desired size.

This is much like ``poster`` does for Postscript files, but working
with PDF. Since sometimes poster does not like your files converted
from PDF. :-) Indeed ``pdfposter`` was inspired by ``poster``.

For more information please refere to the manpage or visit
the `project homepage <https://pdfposter.readthedocs.io/>`_.
"""

from setuptools import setup, find_packages

from distutils.core import Command
from distutils import log
import os, sys

class build_docs(Command):
    description = "build documentation from rst-files"
    user_options=[]

    def initialize_options (self): pass
    def finalize_options (self):
        self.docpages = DOCPAGES
        
    def run(self):
        substitutions = ('.. |VERSION| replace:: '
                         + self.distribution.get_version())
        for writer, rstfilename, outfilename in self.docpages:
            distutils.dir_util.mkpath(os.path.dirname(outfilename))
            log.info("creating %s page %s", writer, outfilename)
            if not self.dry_run:
                try:
                    with open(rstfilename, "rb") as fh:
                        rsttext = fh.read().decode('utf-8')
                except IOError as e:
                    sys.exit(e)
                rsttext = '\n'.join((substitutions, '', rsttext))
                # docutils.core does not offer easy reading from a
                # string into a file, so we need to do it ourself :-(
                doc = docutils.core.publish_string(source=rsttext,
                                                   source_path=rstfilename,
                                                   writer_name=writer)
                try:
                    with open(outfilename, 'wb') as fh:
                        fh.write(doc) # is already encoded
                except IOError as e:
                    sys.exit(e)

cmdclass = {}

try:
    import docutils.core
    import docutils.io
    import docutils.writers.manpage
    import distutils.command.build
    distutils.command.build.build.sub_commands.append(('build_docs', None))
    cmdclass['build_docs'] = build_docs
except ImportError:
    log.warn("docutils not installed, can not build man pages. "
             "Using pre-build ones.")

DOCPAGES = (
    ('manpage', 'pdfposter.rst', 'docs/pdfposter.1'),
    ('html', 'pdfposter.rst', 'docs/pdfposter.html'),
    )

setup(
    cmdclass=cmdclass,
    name = "pdftools.pdfposter",
    version='0.7',
    install_requires = ['PyPDF2'],

    packages=['pdftools.pdfposter'],
    namespace_packages=['pdftools'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
        },

    # metadata for upload to PyPI
    author = "Hartmut Goebel",
    author_email = "h.goebel@crazy-compilers.com",
    description = "Scale and tile PDF images/pages to print on multiple pages.",
    long_description = __doc__,
    license = "GPL 3.0",
    keywords = "pdf poster",
    url          = "https://pdfposter.readthedocs.io/",
    download_url = "https://pypi.org/project/pdftools.pdfposter/",
    classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Printing',
    'Topic :: Utilities',
    ],

    # these are for easy_install (used by bdist_*)
    zip_safe = True,
    entry_points = {
        "console_scripts": [
            "pdfposter = pdftools.pdfposter.cmd:run",
        ],
    },
)
