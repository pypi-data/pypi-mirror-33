Introduction
============

Tinytools is a collection of small, high-level tools that fill gaps in Python 
tool sets.  The tools are broken up into a set of modules

1.  ``bunch`` :  Contains an OrderedBunch object class with associated
    bunchify/unbunchify methods, similar to other bunch implementations but
    built off an OrderedDict with ipython table-complete overloaded to the
    data memebers.
2.  ``files`` :  High-level filter and search functions with configurable
    search depth, case sensitivity, and search types.
3.  ``cmd_list`` :  Thin wrapper around subprocess to simplify command line
    calls.
4.  ``pvl`` : Function to read and write
    `PVL files <https://en.wikipedia.org/wiki/Parameter_Value_Language>`_.
5.  ``class_csv`` : Functions to move columns in csv files - a common need
    for moving class-attributed csv files between machine learning tools.
6.  ``np_img`` :    Numpy operations to flip images - i.e. converting a
    numpy image array from (4,200,200) to (200,200,4).
7.  ``py_styles`` : Display of python style suggestions.

Installing
==========

.. code:: python 

    pip install tinytools

Import
=======

.. code:: python 

    import tinytools

or in a more convenient alias:

.. code:: python

    import tinytools as tt

Quick Start
===========
.. code:: python

    import tinytools as tt

    ## Search function
    found = tt.files.search('/path/to/search',['*.til','proj1*.til'],depth=5,
                                                        case_sensitive=False)

    ## OrderedBunch
    from collections import OrderedDict

    # Create an OrderedBunch from and return it to an OrderedDict
    od = OrderedDict({'a':1,'b':2,'c':{'aa':1.23,'bb':'string'}})
    ob = tt.bunch.ordered_bunchify(od)
    ob.a          # Explore the OrderdBunch with tab complete
    ob['a']       # Equivalent to above
    ob.c.bb       # orderd_bunchify is recursive on nested Dict objects
    ob['c']['bb'] # Equivalent to above
    od2 = tt.bunch.ordered_unbunchify(ob)

    ## Interacting with PVL files
    # Read full PVL file
    imd = tt.pvl.read_from_pvl('/path/to/image.IMD')
    type(imd)                               # returns collections.OrderedDict
    imdob = tt.bunch.ordered_bunchify(img)  # Create an ordered bunch to ease 
                                            # interactive exploration
    imdob.IMAGE_1.satID                     # Tab complete through the IMD files

    # Read an item from a PVL file
    tt.pvl.read_from_pvl('/path/to/image.IMD','satId') # return same as above
    tt.pvl.read_from_pvl('/path/to/image.IMD','ULLon') # return a list of all
                                                       # items matching key
