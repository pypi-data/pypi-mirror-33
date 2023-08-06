# -*- coding: utf-8 -*-
"""tigereye plotting module."""

from __future__ import (absolute_import, division,
    print_function)

import os
import re
import copy

from .error import UsageError
from .util import (error_exit, teye_eval, parse_funcargs, get_var,
    get_axis, get_name, read_template, args_pop)
from .parse import teye_parse

# TODO: use utility functiion for attrs set attrs[key] = value
# TODO: the utility function should check security

def gen_plot(args, attrs):

    # plotting
    plots = []
    if args.plot:
        for plot in args.plot:

            ax, plotarg = get_axis(plot)

            poscomma = plotarg.find(',')
            if poscomma<0:
                raise UsageError('Wrong plot option: %s'%plotarg)
            else:
                pname = plotarg[:poscomma]
                pargs = plotarg[poscomma+1:]
                plot_handle = teye_eval('%s.%s(%s)'%(ax, pname, pargs), attrs)

                try:
                    for p in plot_handle:
                        plots.append(p)
                except TypeError:
                    plots.append(plot_handle)

                if pname == 'pie':
                    attrs[ax].axis('equal')

    if 'plots' in attrs:
        attrs['plots'].extend(plots)
    else:
        attrs['plots'] = plots

def axes_main_functions(args, attrs):

    # title setting
    if args.title:
        for title_arg in args.title:
            ax, title = get_axis(title_arg)
            teye_eval('%s.set_title(%s)'%(ax, title), attrs)


    # x-axis setting
    if args.xaxis:
        for xaxis_arg in args.xaxis:
            ax, xaxis = get_axis(xaxis_arg)

            set_xfuncs =  dict((x, getattr(attrs[ax], x)) for x in dir(attrs[ax]) if x.startswith('set_x'))
            vargs, kwargs = parse_funcargs(xaxis, attrs)

            for name, func in set_xfuncs.items():
                funckey = name[5:] # set_x functions
                if funckey in kwargs:
                    func_args = dict(kwargs)
                    value = func_args.pop(funckey)
                    func(value, **func_args)

    # y-axis setting
    if args.yaxis:
        for yaxis_arg in args.yaxis:
            ax, yaxis = get_axis(yaxis_arg)

            set_yfuncs =  dict((y, getattr(attrs[ax], y)) for y in dir(attrs[ax]) if y.startswith('set_y'))
            vargs, kwargs = parse_funcargs(yaxis, attrs)

            for name, func in set_yfuncs.items():
                funckey = name[5:]
                if funckey in kwargs:
                    func_args = dict(kwargs)
                    value = func_args.pop(funckey)
                    func(value, **func_args)

    # z-axis setting
    if args.zaxis:
        for zaxis_arg in args.zaxis:
            ax, zaxis = get_axis(zaxis_arg)

            set_zfuncs =  dict((z, getattr(attrs[ax], z)) for z in dir(attrs[ax]) if z.startswith('set_z'))
            vargs, kwargs = parse_funcargs(zaxis, attrs)

            for name, func in set_zfuncs.items():
                funckey = name[5:]
                if funckey in kwargs:
                    func_args = dict(kwargs)
                    value = func_args.pop(funckey)
                    func(value, **func_args)

    # grid setting
    if args.g:
        for key in attrs:
            if key=='ax' or (key.startswith('ax') and int(key[2:]) >= 0):
                attrs[key].grid()

    if args.grid:
        for grid_arg in args.grid:
            if grid_arg:
                ax, grid = get_axis(grid_arg)
                teye_eval('%s.grid(%s)'%(ax, grid), attrs)

    # legend setting 
    if args.l:
        for key in attrs:
            if key=='ax' or (key.startswith('ax') and int(key[2:]) >= 0):
                attrs[key].legend()

    if args.legend:
        for legend_arg in args.legend:
            if legend_arg:
                ax, legend = get_axis(legend_arg)
                teye_eval('%s.legend(%s)'%(ax, legend), attrs)


def teye_plot(args, attrs):

    # pages setting
    if args.pages:
        vargs, kwargs = parse_funcargs(args.pages, attrs)

        if vargs:
            attrs['num_pages'] = vargs[-1]
        else:
            attrs['num_pages'] = 1

        for key, value in kwargs.items():
            attrs[key] = value
    else:
        attrs['num_pages'] = 1

    for idx in range(attrs['num_pages']):

        attrs['page_num'] = idx

        if args.page_calc:
            for page_calc in args.page_calc:
                vname, formula = get_var(page_calc)
                attrs[vname] = teye_eval(formula, attrs)


        # figure setting
        if 'figure' in attrs and attrs['figure']:
            pass
        elif args.f:
            attrs['figure'] = teye_eval('pyplot.figure(%s)'%args.f, attrs)
        else:
            attrs['figure'] = attrs['pyplot'].figure()


        # import plot
        if args.import_plot:
            for import_plot_opt in args.import_plot:
                importplots, import_args = [i.strip() for i in import_plot_opt.split('=', 1)]
                newattrs = copy.copy(attrs)
                templates, kwargs = parse_funcargs(import_args, newattrs)
                if len(templates) == 2:
                    opts = read_template(templates[1])
                    if args.noshow:
                        opts.append("--noshow")
                    args_pop(opts, '--book', 1)
                    newargs = teye_parse(opts, newattrs)
                    newattrs.update(kwargs)
                    teye_plot(newargs, newattrs)
                    if importplots:
                        for ppair in importplots.split(','):
                            ppair = ppair.split(':')
                            if len(ppair) == 1:
                                attrs[ppair[0].strip()] = newattrs[ppair[0].strip()]
                            elif len(ppair) == 2:
                                attrs[ppair[0].strip()] = newattrs[ppair[1].strip()]
                            else:
                                raise UsageError('The syntax of importing plot is not correct: %s'%importplots)
                        if 'plots' in newattrs:
                            if 'plots' in attrs:
                                attrs['plots'].extend(newattrs['plots'])
                            else:
                                attrs['plots'] = newattrs['plots']
                    else:
                        raise UsageError('The syntax of import plot is not correct: %s'%importplots)
                else:
                    raise UsageError('The syntax of import plot is not correct: %s'%import_args)

        # plot axis
        if args.ax:
            for ax_arg in args.ax:
                axname, others = get_axis(ax_arg, delimiter='=')
                if axname:
                    vargs, kwargs = parse_funcargs(others, attrs)
                    if 'projection' in kwargs and kwargs['projection'] == '3d':
                         from mpl_toolkits.mplot3d import Axes3D
                         attrs['Axes3D'] = Axes3D
                    if len(vargs) == 0 or not isinstance(vargs[0], int):
                        attrs[axname] = teye_eval('figure.add_subplot(111, %s)'%others, attrs)
                    else:
                        attrs[axname] = teye_eval('figure.add_subplot(%s)'%others, attrs)
                else:
                    raise UsageError('Wrong axis option: %s'%ax_arg)
        elif not args.import_plot:
            attrs['ax'] = attrs['figure'].add_subplot(111)

        # page names
        if 'page_names' in attrs:
            page_names = attrs['page_names']
            if callable(page_names):
                attrs['page_name'] = page_names(attrs['page_num'])
            else:
                attrs['page_name'] = page_names[attrs['page_num']]
        else:
            attrs['page_name'] = 'page%d'%(attrs['page_num'] + 1)

        # execute figure functions
        if args.figure:
            for fig_arg in args.figure:
                name, others = get_name(fig_arg)
                if others:
                    teye_eval('figure.%s(%s)'%(name, others), attrs)
                else:
                    teye_eval('figure.%s()'%name, attrs)

        # generate plots
        gen_plot(args, attrs)

        # selected axes functions
        axes_main_functions(args, attrs)

        # execute axes functions
        if args.axes:
            for axes_arg in args.axes:
                ax, arg = get_axis(axes_arg)
                name, others = get_name(arg)
                if others:
                    teye_eval('%s.%s(%s)'%(ax, name, others), attrs)
                else:
                    teye_eval('ax.%s()'%name, attrs)
        elif not attrs['plots']:
            if len(attrs['_data_objects']) > 0:
                for data_obj in attrs['_data_objects']:
                    attrs['ax'].plot(data_obj.get_data('', '', attrs))
            elif not args.figure:
                error_exit("There is no data to plot.")

        # saving an image file
        if args.save:
            for save_arg in args.save:
                name, others = get_name(save_arg)
                if attrs['num_pages'] > 1:
                    root, ext = os.path.splitext(name)
                    name = '%s-%d%s'%(root, attrs['page_num'], ext)
                if others:
                    others = ', %s'%others
                if '_pdf_pages' in attrs:
                    if attrs['_page_save']:
                        teye_eval('figure.savefig(%s%s)'%(name, others), attrs)
                    teye_eval('_pdf_pages.savefig(figure=figure)', attrs)
                else:
                    teye_eval('figure.savefig(%s%s)'%(name, others), attrs)

        # displyaing an image on screen
        if not args.noshow:
            attrs['pyplot'].show()

        teye_eval('pyplot.close(figure)', attrs)

