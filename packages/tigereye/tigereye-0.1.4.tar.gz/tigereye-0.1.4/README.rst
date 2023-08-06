========
tigereye
========


.. image:: https://img.shields.io/pypi/v/tigereye.svg
        :target: https://pypi.python.org/pypi/tigereye

.. image:: https://img.shields.io/travis/grnydawn/tigereye.svg
    :target: https://travis-ci.org/grnydawn/tigereye


A reusable data-manipulation and plotting tool

* Free software: MIT license
* Documentation: https://grnydawn.github.io/tigereyedocs.


-----------------
What is tigereye?
-----------------

Tigereye is a portable command-line utility for creating plots from various sources of data.  It advocates incremental plotting that you can immediately see the effect of changes made in command-line. Until satisfied, you can generate plots through a very quick cycle of "change-run-see". In addition, tigereye can read data of various formats, compactly modify them on command-line, and output modified data as the form of plots as well as texts. Tigereye also supports importing both of plots and data that could be created independently.

------------
Installation
------------

Dependencies
============

Tigereye extensively uses matplotlib_ and numpy_ Python packages. Before using tigereye, the two Python packages need to be installed. In many cases, the packages may be already available for you. You can check if the packages are available locally on your computer by running following commands. You should see three numbers similar to "2.2.2" per each commands below. If not, please visit corresponding package site and follow installation direction to install.

.. code-block:: text

    $ python -c "import numpy; print(numpy.__version__)"
    $ python -c "import matplotlib; print(matplotlib.__version__)"

You can install tigereye either using pip Python package manager or using source code from github repositiory. You may get a stable version from using pip and a latest version from using source code.

Installing tigereye using pip
=============================

.. code-block:: text

    $ pip install tigereye
    $ tigereye --version

Installing tigereye from github repository
==========================================

.. code-block:: text

    $ git clone https://github.com/grnydawn/tigereye.git
    $ cd tigereye
    $ python setup.py install
    $ tigereye --version

----------------
Simple examples
----------------

The simplest tigereye plot
==========================

.. code-block:: text

    $ tigereye "[1,2,4]"

A title is added.
=================

.. code-block:: text

    $ tigereye "[1,2,4]" \
        -t "'Sample Plot', fontsize=16"

Labels are added into x and y axes.
===================================

.. code-block:: text

    $ tigereye "[1,2,4]" \
        -t "'Sample Plot', fontsize=16" \
        -x "label='X', fontsize=12" \
        -y "label='Y', fontsize=12"

Data is generated using numpy.
==============================

.. code-block:: text

    $ tigereye \
        -v "varx=numpy.linspace(0, 2*numpy.pi)" \
        -v "vary=numpy.sin(varx)" \
        -t "'Sample Plot', fontsize=16" \
        -x "label='X', fontsize=12" \
        -y "label='Y', fontsize=12" \
        -p "plot, varx, vary, label='line1'"

Plot is generated using a template .
====================================

.. code-block:: text

    $ tigereye \
        -i https://raw.githubusercontent.com/grnydawn/tigereye/master/template/basic/sample1.tgr \
        -t "'My Plot'"

Data is read from a local file.
===============================

.. code-block:: text

    $ echo $'1,2,3\n4,5,6\n7,8,9' > simple.csv
    $ tigereye simple.csv \
        --data-format "numpytext, delimiter=','" \
        -v "row0=d0[0,:]" \
        -v "row1=d0[1,:]" \
        -v "row2=d0[2,:]" \
        -t "'Sample Plot', fontsize=16" \
        -x "label='X', fontsize=12" \
        -y "label='Y', fontsize=12" \
        -p "plot, row0, row2, label='line-1'" \
        -p "bar, row0, row1, width= 0.5, label='bar-1'" \
        -g \
        -l

Data is read from online.
===============================

.. code-block:: text

    $ tigereye https://raw.githubusercontent.com/grnydawn/tigereye/master/data/simple.csv \
        --data-format "numpytext, delimiter=','" \
        -v "row0=d0[0,:]" \
        -v "row1=d0[1,:]" \
        -v "row2=d0[2,:]" \
        -t "'Sample Plot', fontsize=16" \
        -x "label='X', fontsize=12" \
        -y "label='Y', fontsize=12" \
        -p "plot, row0, row2, label='line-1'" \
        -p "bar, row0, row1, width= 0.5, label='bar-1'" \
        -g \
        -l

Multi-page PDF file is generated .
==================================

.. code-block:: text

    $ tigereye https://raw.githubusercontent.com/grnydawn/tigereye/master/data/simple.csv \
        --data-format "numpytext, delimiter=','" \
        -x "label='X', fontsize=12" \
        -y "label='Y', fontsize=12" \
        --pages "len(d0), pdf_merge=True" \
        -p "plot, numpy.arange(len(d0)), d0[page_num, :], label='line-%d'%page_num" \
        -t "'Page-%d'%page_num" \
        -s "'sample.pdf'" \
        --noshow \
        -g \
        -l

---------------
Further reading
---------------

    tigereye_ Documentation

--------------
Acknowledgment
--------------

Tigereye extensively uses matplotlib_ and numpy_. The packages have vastly accepted by community with reasons. Tigereye could be considered as a wrapper of several well-known Python packages including matplotlib_ and numpy_.

.. _matplotlib: https://matplotlib.org/
.. _numpy: http://www.numpy.org/
.. _tigereye: https://grnydawn.github.io/tigereyedocs
