========================
``wil`` -- Will it link?
========================

This is a proof of concept for the ``willitlink`` project.


Quick Start
-----------

Collect the data from scons (does a full build).  Note the quote around the scons flags.  deps.json and dependency_tree.txt are intermediate files to be used in the next command.

::

   python wil.py collect -m <path_to_mongodb_repo> --tree_name <path_to_willitlink>/data/dependency_tree.txt --data <path_too_willitlink>/data/deps.json --scons "<scons_flags>"

Complete the initial data processing and make the result dataset.

::

   python wil.py ingest -t -m <path_to_mongodb_repo> --input_tree <path_to_willitlink>/data/dependency_tree.txt --dep_info <path_to_willitlink>/data/deps.json --output_dep_name <path_to_willitlink>/data/dep_graph.json

Example Queries
~~~~~~~~~~~~~~~

Get all symbols needed by this archive that are not defined by this archive or anything it depends on (meaning that this archive will not link on its own).

::

    python wil.py -t tree --leak libmongocommon.a 2

Get all libraries needed by this archive.  The "bad" entry in the dictionary represents a symbol that is defined in more than one place, which means that "one of these archives" is needed to link.

::

    python wil.py -t libs-needed libmongocommon.a

Get circular dependencies for the library.

::

    python wil.py -t libs-cycle liblasterror.a
