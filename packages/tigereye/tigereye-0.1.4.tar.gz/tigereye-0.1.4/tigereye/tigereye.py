# -*- coding: utf-8 -*-
"""tigereye main module."""
from __future__ import absolute_import

import copy

# import tigereye features
from .util import (support_message, error_exit, parse_funcargs, teye_eval,
    read_template, args_pop)
from .error import InternalError, UsageError
from .parse import teye_parse
from .load import teye_load
from .var import teye_var
from .plot import teye_plot

def entry():
    import sys
    return main(sys.argv[1:])

def main(argv):

    try:

        # plotting environment
        attrs = {}

        # import core libraries
        import os
        import numpy
        # folloing if block should be located "before" any matlablib use
        if os.environ.get('DISPLAY','') == '':
            import matplotlib
            matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        attrs['numpy'] = numpy
        attrs['pyplot'] = plt

        # argument and template processing
        #argv = [item.decode("utf-8") for item in argv]
        args = teye_parse(argv, attrs)

        # data collection
        teye_load(args, attrs)

        # plotting variables
        teye_var(args, attrs)

        # exit if noplot option exists
        if 'return' in attrs:
            return attrs['return']

        # multipage
        if args.book:
            vargs, kwargs = parse_funcargs(args.book, attrs)
            if vargs:
                bookfmt = kwargs.pop('format', 'pdf').lower()
                attrs['_page_save'] = kwargs.pop('page_save', False)
                kwargs = ', '.join(['%s=%s'%(k,v) for k,v in kwargs.items()])
                if kwargs:
                    kwargs = ', %s'%kwargs
                for target in vargs:
                    if bookfmt == 'pdf':
                        from matplotlib.backends.backend_pdf import PdfPages
                        attrs['_pdf_pages'] =  teye_eval('_p("%s"%s)'%(target, kwargs), attrs, _p=PdfPages)
                    else:
                        raise UsageError('Book format, "%s", is not supported.'%bookfmt)

        attrs_save = copy.copy(attrs)
        if args.front_page:
            for front_page_opt in args.front_page:
                newattrs = copy.copy(attrs)
                templates, kwargs = parse_funcargs(front_page_opt, newattrs)
                if len(templates) == 1:
                    opts = read_template(templates[0])
                    if args.noshow:
                        opts.append("--noshow")
                    if args.save:
                        for save_opt in args.save:
                            opts.extend(["--save", save_opt])
                    args_pop(opts, '--book', 1)
                    newargs = teye_parse(opts, newattrs)
                    newattrs.update(kwargs)
                    teye_load(newargs, newattrs)
                    teye_var(newargs, newattrs)
                    teye_plot(newargs, newattrs)
                else:
                    raise UsageError('The syntax of import plot is not correct: %s'%import_args)

        # plot generation
        teye_plot(args, attrs)

        if args.back_page:
            for back_page_opt in args.back_page:
                newattrs = attrs_save
                templates, kwargs = parse_funcargs(back_page_opt, newattrs)
                if len(templates) == 1:
                    opts = read_template(templates[0])
                    if args.noshow:
                        opts.append("--noshow")
                    if args.save:
                        for save_opt in args.save:
                            opts.extend(["--save", save_opt])
                    args_pop(opts, '--book', 1)
                    newargs = teye_parse(opts, newattrs)
                    newattrs.update(kwargs)
                    teye_load(newargs, newattrs)
                    teye_var(newargs, newattrs)
                    teye_plot(newargs, newattrs)
                else:
                    raise UsageError('The syntax of import plot is not correct: %s'%import_args)

        # multi-page closing
        if '_pdf_pages' in attrs:
            attrs['_pdf_pages'].close()

    except InternalError as err:

        print(err.error_message())
        error_exit(support_message())

    except UsageError as err:

        print(err.error_message())
        error_exit(args.usage())

    except ImportError as err:

        error_exit(str(err))

    else:
        return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))
