==========================
pdfposter
==========================

-------------------------------------------------------------
Scale and tile PDF images/pages to print on multiple pages.
-------------------------------------------------------------

:Author:    Hartmut Goebel <h.goebel@crazy-compilers.com>
:Version:   Version 0.7
:Copyright: 2008-2018 by Hartmut Goebel
:Licence:   GNU Public Licence v3 (GPLv3)
:Homepage:  https://pdfposter.readthedocs.io/

``Pdfposter`` can be used to create a large poster by building it from
multiple pages and/or printing it on large media. It expects as input a
PDF file, normally printing on a single page. The output is again a
PDF file, maybe containing multiple pages together building the
poster.
The input page will be scaled to obtain the desired size.

This is much like ``poster`` does for Postscript files, but working
with PDF. Since sometimes poster does not like your files converted
from PDF. :-) Indeed ``pdfposter`` was inspired by ``poster``.

For more information please refer to the manpage or visit
the `project homepage <https://pdfposter.readthedocs.io/>`_.


Requirements and Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Pdfposter`` requires

* `Python`__  (tested 2.7 and 3.4—3.6, but newer versions should work, too),
* `setuptools`__ or `pip`__ for installation, and
* `PyPDF2`__.

__ https://www.python.org/download/
__ https://pypi.org/project/setuptools
__ https://pypi.org/project/pip
__ http://mstamy2.github.io/PyPDF2/


.. Emacs config:
 Local Variables:
 mode: rst
 End:
