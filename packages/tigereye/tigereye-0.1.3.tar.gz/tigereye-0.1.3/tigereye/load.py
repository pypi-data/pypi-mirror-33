# -*- coding: utf-8 -*-
"""tigereye data read module."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import re
import shlex
import abc
import tempfile

from .error import UsageError
from .util import PY3, temp_attrs, teye_eval, teye_exec, error_exit

_re_datafmt = re.compile(r'(d(?P<data>\d+)\s*:)?\s*(?P<format>\w+)\s*,\s*(?P<others>.*)')

def _get_format(arg):
    if match:
        return match.group('ax'), match.group('others')
    else:
        return 'ax', arg

# numpyarray

# csv

# numpytext

# panda
# -read_csv
# -read_json
# -read_html
# -read_clipboard
# -read_excel
# -read_hdf
# -read_feather
# -read_parquet
# -read_msgpack
# -read_stata
# -read_sas
# -read_pickle
# -read_sql
# -read_gbq

# netcdf

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

def _subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _subclasses(c)])

class Data(object):

    __metaclass__ = abc.ABCMeta

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        if self.data is None:
            return 0
        else:
            return len(self.data)

    @abc.abstractmethod
    def _lib_item(self, vname, cmd, attrs):
        pass

    @abc.abstractmethod
    def _lib_func(self, vname, cmd, params, attrs):
        pass

    def get_data(self, vname, arg, attrs):

        data = self.data
        if vname:
            attrs[vname] = data

        while arg:
            cmd, params, arg = self._parse_arg(arg)
            if cmd[0] == '[' and cmd[-1] == ']':
                data = self._lib_item(vname, cmd, attrs)
            elif cmd == 'dict':
                data = self._dict(vname, params, attrs)
            else:
                data = self._lib_func(vname, cmd, params, attrs)
            if self.data is None:
                self.data = data
            if vname:
                attrs[vname] = data

        return data

    def _parse_arg(self, arg):

        cmd = []
        params = []
        others = []

        stack = []
        remained = False

        arg = arg.replace(' ', '__WS__')

        for item in shlex.shlex(arg):

            if remained:
                others.append(item)
                continue

            if stack:
                if item == '(':
                    if stack:
                        params.append(item)
                    stack.append(item)
                elif item == ')':
                    stack.pop()
                    if stack:
                        params.append(item)
                    else:
                        remained = True
                else:
                    params.append(item)
            else:
                if item == '(':
                    stack.append(item)
                elif item == '.':
                    remained = True
                elif item == ')':
                    raise UsageError('Wrong data input syntax: %s'%arg)
                else:
                    cmd.append(item)

        if others and others[0] == ".":
            others = others[1:]

        return (''.join(cmd).replace('__WS__', ' '),
            ''.join(params).replace('__WS__', ' '),
            ''.join(others).replace('__WS__', ' '))

    def _dict(self, vname, params, attrs):
        newattrs = temp_attrs(attrs, [('_f_', dict)])
        output = teye_eval('_f_(%s)'%params, g=newattrs)
        if output is not None:
            return output
        else:
            return newattrs[vname]

# handler types

class FileData(Data):
    pass

class ValueData(Data):
    pass

# mixins

class RemoteDataMixin(object):

    def  _download(self, datasrc):

        data = None

        try:
            if urlparse(datasrc).netloc:
                f = urlopen(datasrc)
                data = f.read()
                f.close()
        except HTTPError, e:
            error_exit("HTTP Error: %s %s"%(str(e.code), datasrc))
        except URLError, e:
            error_exit("URL Error: %s %s"%(str(e.reason), datasrc))

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(data)
        return f.name

class BuildMixin(object):

    def __init__(self):
        self.data = None

class NumpyMixin(object):

    def _lib_item(self, vname, cmd, attrs):
        return teye_eval(vname+cmd, g=attrs)

    def _lib_func(self, vname, cmd, params, attrs):
        func = attrs['numpy']
        for name in cmd.split('~'):
            func = getattr(func, name)
        newattrs = temp_attrs(attrs, [('_f_', func)])
        output = teye_eval('_f_(%s)'%params, g=newattrs)
        if output is not None:
            return output
        else:
            return newattrs[vname]


# numpy handlers

class NumpyArrayData(NumpyMixin, ValueData):

    name = 'numpyarray'

    def __init__(self, datasrc, args, attrs):
        if args:
            self.data = teye_eval('numpy.asarray(%s, %s)'%(datasrc, args), g=attrs)
        else:
            self.data = teye_eval('numpy.asarray(%s)'%datasrc, g=attrs)

class NumpyBuildData(NumpyMixin, BuildMixin, ValueData):

    name = 'numpybuild'


class NumpyTextData(NumpyMixin, FileData, RemoteDataMixin):

    name = 'numpytext'

    def __init__(self, datasrc, args, attrs):

        fname = None

        if os.path.isfile(datasrc):
            fname = datasrc
        elif urllib_imported:
            fname = self._download(datasrc)

        if fname:
            kwargs = ''
            if args:
                kwargs += ', %s'%args

            self.data = teye_eval("numpy.genfromtxt('%s'%s)"%(fname, kwargs), g=attrs)
        else:
            error_exit("Input argument syntax error: '%s, %s'"%(datasrc, args))

class CsvTextData(NumpyMixin, FileData, RemoteDataMixin):

    name = 'csv'

    def __init__(self, datasrc, args, attrs):

        fname = None

        if os.path.isfile(datasrc):
            fname = datasrc
        elif urllib_imported:
            fname = self._download(datasrc)

        if fname:
            kwargs = ', dtype=object'
            if not args or 'delimiter' not in args:
                kwargs += ", delimiter=','"

            if args:
                kwargs += ', %s'%args
            self.data = teye_eval("numpy.genfromtxt('%s'%s)"%(fname, kwargs), g=attrs)
        else:
            error_exit("Input argument syntax error: '%s, %s'"%(datasrc, args))

# handler groups
_file_format_handlers = list(
    cls for cls in _subclasses(FileData) if hasattr(cls, 'name'))
_value_format_handlers = list(
    cls for cls in _subclasses(ValueData) if hasattr(cls, 'name'))
_build_handlers = dict(
    (cls.name, cls) for cls in _subclasses(BuildMixin) if hasattr(cls, 'name'))
_data_handlers = dict(
    (cls.name, cls) for cls in _subclasses(Data) if hasattr(cls, 'name'))

def _select_srcfmt(datasrc, attrs):
    if os.path.isfile(datasrc):
        for cls in _file_format_handlers:
            try:
                return cls(datasrc, None, attrs)
            except:
                pass
    else:
        for cls in _value_format_handlers:
            try:
                return cls(datasrc, None, attrs)
            except:
                pass

def teye_load(args, attrs):

    _data_objects = []

    # read data files
    if args.data_sources:
        srcfmts = [None for _ in range(len(args.data_sources))]
        global_fmt = None

        # format: 0:name, ... or name, ...
        if args.data_format:
            for fmt in args.data_format:
                match = _re_datafmt.match(fmt)
                if match:
                    did, fmt, others = match.group('data'), match.group('format'), match.group('others')
                    handler = _data_handlers[fmt]
                    if did:
                        srcfmts[int(did)] = (handler, others)
                    else:
                        global_fmt = (handler, others)
                else:
                    print('Warning: source format syntax error (ignored): %s'%fmt)

        if global_fmt is not None:
            for idx in range(len(args.data_sources)):
                if srcfmts[idx] is None:
                    srcfmts[idx] = global_fmt

        for idx, data_source in enumerate(args.data_sources):

            if srcfmts[idx] is None:
                data = _select_srcfmt(data_source, attrs)
            else:
                data = srcfmts[idx][0](data_source, srcfmts[idx][1], attrs)

            if data:
                attrs['d%d'%idx] = data
                _data_objects.append(data)
            else:
                raise UsageError('"%s" is not loaded correctly.'%data_source)

    attrs['_build_handlers'] = _build_handlers

    attrs['_data_objects'] = _data_objects
