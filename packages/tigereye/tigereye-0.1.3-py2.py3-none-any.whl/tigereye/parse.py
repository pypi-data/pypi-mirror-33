# -*- coding: utf-8 -*-
"""tigereye argument parsing module."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import sys
import shlex
import argparse
import tempfile

from .util import PY3

try:
    if PY3:
        from urllib.request import urlopen
        from urllib.parse import urlparse
    else:
        from urllib2 import urlopen
        from urlparse import urlparse
    urllib_imported = True
except ImportError as e:
    urllib_imported = False

class ArgParse(object):

    def __init__(self, argv):

        self._template, newargv = self._handle_template(argv)
        self._args = self._parse_arguments(newargv)

    def usage(self):
        return 'Usage: T.B.D.'

    def __str__(self):
        l = [str(self._args)]
        l.append(str(self._template))
        return '\n'.join(l)

    def __getattr__(self, name):

        if name in self._args:
            if self._args[name] is None:
                if self._template is not None:
                    return getattr(self._template, name)
            else:
                return self._args[name]
            return None

        raise AttributeError(
            "AttributeError: 'ArgParse' object has no attribute '%s'"%name)

    def __contains__(self, name):

        try:
            getattr(self, name)
            return True
        except AttributeError:
            return False

    def __getitem__(self, name):
        return getattr(self, name)

    def _extract_argument(self, argv, *extract):

        if len(argv) < 2:
            return [], argv

        extracts = [];
        newargv = []
        skip = False

        for arg, nextarg in zip(argv, argv[1:]+[None]):

            if skip:
                skip = False
                continue

            if arg in extract:
                extracts.append(nextarg)
                skip = True
            else:
                newargv.append(arg)

        return extracts, newargv

    def _load_template(self, template):

        data = None

        if os.path.isfile(template):
            with open(template, 'rb') as f:
                data = f.readlines()
        elif urllib_imported:
            try:
                if urlparse(template).netloc:
                    f = urlopen(template)
                    data = f.readlines()
                    f.close()
            except HTTPError, e:
                error_exit("HTTP Error: %s %s"%(str(e.code), template))
            except URLError, e:
                error_exit("URL Error: %s %s"%(str(e.reason), template))
        else:
            error_exit("Input template syntax error: '%s'"%template)

        if data:
            lines = []
            for line in data:
                line = line.strip()
                if line and line[-1] == '\\':
                    line = line[:-1]
                lines.append(line)
            cmdline = ' '.join(lines)
            return teye_parse(shlex.split(cmdline), None)
        else:
            return None

    def _handle_template(self, argv):

        template, newargv = self._extract_argument(argv, "-i", "--import")
        if len(template) > 1:
            error_exit('More than one templates are imported.')
        elif len(template) == 1:
            return self._load_template(template[0]), newargv
        else:
            return None, newargv

    def _parse_arguments(self, argv):

        # TODO: add figure functions
        # TODO: add zaxis support
        # TODO: add page-calc support
        # TODO: add front-page and back-page support
        #       - provides kwargs for data inputs
        #       - data definitions in front-age are overwritten
        #       - tigereye provides input analysis report
        # TODO: add tigereye command-line analysis report
        # TODO: add import-data support

        parser = argparse.ArgumentParser(description='A reusable data-manipulation and plotting tool')
        parser.add_argument('data_sources', metavar='data source', nargs='*', help='input raw data.')
        parser.add_argument('-v', '--variable', metavar='varname:<formula>', action='append', help='define data.')
        parser.add_argument('-t', '--title', metavar='title', action='append', help='title  plotting.')
        parser.add_argument('-p', '--plot', metavar='plot type', action='append', help='plot type for plotting.')
        parser.add_argument('-f', '--figure', metavar='figure', help='figure for plotting.')
        parser.add_argument('-s', '--save', metavar='save', action='append', help='file path to save png image.')
        parser.add_argument('-d', '--value', metavar='value', action='append', help='print data value on screen.')
        parser.add_argument('-x', '--xaxis', metavar='xaxis', action='append', help='axes function wrapper for x axis settings.')
        parser.add_argument('-y', '--yaxis', metavar='yaxis', action='append', help='axes function wrapper for y axis settings.')
        parser.add_argument('-z', '--zaxis', metavar='zaxis', action='append', help='axes function wrapper for z axis settings.')
        parser.add_argument('-i', '--import', metavar='template', help='importing a tigereye template')
        parser.add_argument('-a', '--analysis', metavar='analysis', help='generate tigereye command-line analysis')
        parser.add_argument('-g', action='store_true', help='grid for ax plotting.')
        parser.add_argument('-l', action='store_true', help='legend for ax plotting')
        parser.add_argument('--legend', metavar='legend', action='append', help='plot legend')
        parser.add_argument('--grid', metavar='grid', action='append', help='grid for plotting.')
        parser.add_argument('--ax', metavar='ax', action='append', help='define plot axes.')
        parser.add_argument('--axes', metavar='axes', action='append', help='define Axes function.')
        parser.add_argument('--data-format', metavar='data format', action='append', help='define the format and load options of raw input data.')
        parser.add_argument('--calc', metavar='calc', action='append', help='python code for manipulating data.')
        parser.add_argument('--pages', metavar='pages', help='page settings.')
        parser.add_argument('--page-calc', metavar='page_calc', action='append', help='python code for manipulating data within page generation.')
        parser.add_argument('--front-page', metavar='front_page', action='append', help='importing front page')
        parser.add_argument('--back-page', metavar='back_page', action='append', help='importing back page')
        parser.add_argument('--import-data', metavar='import_data', action='append', help='importing data')
        parser.add_argument('--noshow', action='store_true', default=False, help='prevent showing plot on screen.')
        parser.add_argument('--noplot', action='store_true', default=False, help='prevent generating plot.')
        parser.add_argument('--version', action='version', version='tigereye version %s'%sys.modules['tigereye'].__version__)

        parsed_args = parser.parse_args(argv)

        return dict((k, v) for k, v in parsed_args._get_kwargs())


def teye_parse(argv, attrs):

    args = ArgParse(argv)

    return args
