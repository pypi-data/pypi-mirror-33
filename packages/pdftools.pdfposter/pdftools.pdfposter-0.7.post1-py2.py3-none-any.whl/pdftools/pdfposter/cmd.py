#!/usr/bin/env python
"""
pdftools.pdfposter.cmd - scale and tile PDF images/pages to print on multiple pages.
"""
#
# Copyright 2008-2018 by Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import print_function

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2008-2018 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3)"

from . import main, __version__, DEFAULT_MEDIASIZE, papersizes, DecryptionError
import re
import PyPDF2.utils
import argparse

# pattern for parsing user textual box spec
pat_box = re.compile(r'''
     ( (?P<width>  (\d*\.)? \d+) x                 # width "x" height
       (?P<height> (\d*\.)? \d+) )?
     (?P<offset> \+                                # "+" offset_x "," offset_y
                 (?P<offset_x> \d+\.? | \d*\.\d+)
                 ,
                 (?P<offset_y> \d+\.? | \d*\.\d+) ) ?
     (?P<unit> [a-z][a-z0-9\-\\_]*)                # unit
     ''', re.X+re.I)

def __parse_box(value, allow_offset=False):
    m = pat_box.match(value)
    if not m:
        raise argparse.ArgumentTypeError("I don't understand your box specification %r" % value)
    res = m.groupdict()
    if not allow_offset and res['offset'] is not None:
        raise argparse.ArgumentTypeError('Offset not allowed in box definition')
    # res['offset'] is only used for error checking, remove it
    del res['offset']

    # get meassures of unit
    unit = res['unit'].lower()
    if not unit in papersizes:
        unit = [name for name in papersizes.keys()
                if name.startswith(unit)]
        if len(unit) == 0:
            raise argparse.ArgumentTypeError("I don't understand your papersize name %r" % res['unit'])
        elif len(unit) != 1:
            raise argparse.ArgumentTypeError('Your papersize name %r is not unique, give more chars.' % res['unit'])
        unit = unit[0]
    unit_x, unit_y = papersizes[unit]
    res2 = {
        'width'   : float(res['width'] or 1) * unit_x,
        'height'  : float(res['height'] or 1) * unit_y,
        'offset_x': float(res['offset_x'] or 0) * unit_x,
        'offset_y': float(res['offset_y'] or 0) * unit_y,
        'unit': unit,
        'units_x': float(res['width'] or 1),
        'units_y': float(res['height'] or 1),
        }
    return res2


BoxDefinitionsHelp = """\
A `BOX` to be passed to `--media-size` and `--poster-size` is a specification
of horizontal and vertical size. The syntax is as follows (with multiplier
being specified optionally):

  *box* = [ *multiplier* ] *unit*

  *multiplier* = *number* "x" *number*

  *unit* = *medianame* or *distancename*

Please see `--help-media-size` for a list of media and distance names
supported.

Medias are typically not quadratic but rectangular, which means width
and height differ. Thus using medianames is a bit tricky:

:10x20cm: obvious: 10 cm x 20 cm (portrait)
:20x10cm: same as 10x20cm, since all boxes are rotated to portrait
          format

Now when using media names it gets tricky:

:1x1a4: same as approx. 21x29cm (21 cm x 29 cm, portrait)

:1x2a4: same as approx. 21x58cm (21 cm x 58 cm, portrait)

        This are two a4 pages put together at the *small* side: One
        portrait page wide and two portrait pages high.

:2x1a4: same as approx. 42x29cm, which is rotated to portrait and is
         (approx.) the same as 29x42cm (29 cm x 42 cm)

        This are two a4 pages put together at the *long* side: Two
        portrait pages wide and one portrait page high.
"""

class HelpMediaNames(argparse.Action):
    def __call__(*args, **kw):
        import textwrap
        print('Available media and distance names:')
        names = list(papersizes.keys())
        names.sort()
        for l in textwrap.wrap(' '.join(names), width=65):
            print(' ', l)
        raise SystemExit(0)

class HelpBoxDefinitions(argparse.Action):
    def __call__(*args, **kw):
        import textwrap
        print(textwrap.dedent(BoxDefinitionsHelp))
        raise SystemExit(0)


def run(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument('--help-media-names', action=HelpMediaNames,
                        nargs=0,
                        help='List available media and distance names')
    parser.add_argument('--help-box-definitions', action=HelpBoxDefinitions,
                        nargs=0,
                        help='Show help about specifying BOX for '
                             '`--media-size` and `--poster-size` and exit')
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + __version__)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                      help='Be verbose. Tell about scaling, rotation and number of pages. Can be used more than once to increase the verbosity. ')
    parser.add_argument('-n', '--dry-run', action='store_true',
                      help='Show what would have been done, but do not generate files.')

    group = parser.add_argument_group('Define Input')
    group.add_argument('-f', '--first', type=int, dest='first_page',
                     metavar='INTEGER',
                     help='First page to convert (default: first page)')
    group.add_argument('-l', '--last', type=int, dest='last_page',
                     metavar='INTEGER',
                     help='Last page to convert (default: last page)')
    group.add_argument('-A', '--art-box',
                     action='store_true', dest='use_ArtBox',
                     help='Use the content area defined by the ArtBox '
                     '(default: use the area defined by the TrimBox)')

    group = parser.add_argument_group('Define Target')
    group.add_argument('-m', '--media-size',
                     default=__parse_box(DEFAULT_MEDIASIZE),
                     type=__parse_box, metavar="BOX",
                     help='Specify the page size of the output media (default: %s)' % DEFAULT_MEDIASIZE)
    group.add_argument('-p', '--poster-size',
                     type=__parse_box, metavar="BOX",
                     help='Specify the poster size (defaults to media size). ')
    group.add_argument('-s', '--scale', type=float,
                     help='Specify a linear scaling factor to produce the poster.')

    parser.add_argument('infilename', metavar='InputFile')
    parser.add_argument('outfilename', metavar='OutputFile')

    args = parser.parse_args(args)

    if args.scale is not None and args.poster_size is not None:
        parser.error('Only one of -p/--poster-size and -s/--scale may be given at a time.')
    if not args.poster_size:
        args.poster_size = args.media_size.copy()
    if args.scale is not None:
        args.poster_size = None
        if args.scale < 0.01:
            parser.error("Scale value is much to small: %s" % args.scale)
        elif args.scale > 1.0e6:
            parser.error("Scale value is much to big: %s" % args.scale)

    try:
        main(args, infilename=args.infilename, outfilename=args.outfilename)
    except DecryptionError as e:
        raise SystemExit(str(e))
    except PyPDF2.utils.PdfReadError as e:
        parser.error('The input-file is either currupt or no PDF at all: %s'
                     % e)


if __name__ == '__main__': # pragma: no cover
    run()
