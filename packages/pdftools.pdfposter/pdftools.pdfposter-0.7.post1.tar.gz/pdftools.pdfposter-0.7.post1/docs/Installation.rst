
Download & Installation
=========================

Instructions for Windows Users
-----------------------------------

1. |pdfposter| requires Python. If you don't have Python installed already,
   download and install Python 3.6 from https://python.org/download/3.6/

   During installation, make sure to check "Include into PATH".

2. If you already have Python installed, please check that your Python
   directory (normally :file:`C:\\Python36` for python 3.6) and the Python
   Scripts directory (normally :file:`C:\\Python36\\Scripts`) are in the system
   path. If not, just add them in :menuselection:`My Computer --> Properties
   --> Advanced --> Environment Variables` to the :envvar:`Path` system
   variable.

3. Install |pdfposter| by running ::

     pip install pdftools.pdfposter

   Then run the console command ``pdfposter --help`` to get detailed help.

   If the command ``pip`` is unknown to you system, please refer to the
   `pip homepage <https://pip.pypa.io/en/stable/installing/>`_ for help.


Instructions for GNU/Linux and other Operating Systems
--------------------------------------------------------

Most current GNU/Linux distributions provide packages for |pdfposter|.
Simply search your distribution's software catalog.

Also many vendors provide Python, and some even provide |pdfposter|.
Please check your vendor's software repository.

If your distribution or vendor does not provide a current version of
|pdfposter| please read on.

If your vendor does not provide :command:`python`
please download Python 3.6 from https://www.python.org/download/ and
follow the installation instructions there.

If you distribution or vendor missed providing :command:`pip`,
alongside :command:`python`,
please check your vendor's or distribution's software repository
for a package called `pip` or `python-pip`.
If this is not provided, please refer to the
`pip homepage <https://pip.pypa.io/en/stable/installing/>`_ for help.


Optionally you might want to install `PyPDF2`
- which is a requirement for |pdfposter| -
provided by your distribution or vendor
so at least this package will be maintained by your distribution.
Check for a package named ``python-pypdf2`` or that like.

Then continue with :ref:`installing pdfposter` below.


.. _installing pdfposter:

Installing |pdfposter| using :command:`pip`
---------------------------------------------

After installing `Python` (and optionally `PyPDF2`), just run::

  sudo pip install pdftools.pdfposter

to install |pdfposter| for all users.
For installing |pdfposter| for yourself only, run::

  pip install --user pdftools.pdfposter

If your system does not have network access
  
- download |pdfposter| from https://pypi.org/project/pdftools.pdfposter/,

- downlaod `PyPDF2` from https://pypi.org/project/PyPDF2/, and

- run ::

    sudo pip install pdftools.pdfposter-*.tar.gz PyPDF2-*.tar.gz

  respective ::

    pip install --user pdftools.pdfposter-*.tar.gz PyPDF2-*.tar.gz


.. include:: _common_definitions.txt

