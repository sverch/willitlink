========================
``wil`` -- Will it link?
========================

This is a proof of concept for the ``willitlink`` project.


Quick Start
-----------

::

   bash <path to repo>/willitlink\_gen.sh <scons flags>

Build MongoDB with SSL
~~~~~~~~~~~~~~~~~~~~~~

::

   bash ~/projects/willitlink/willitlink\_gen.sh --ssl --dd --mute --cpppath /usr/local/Cellar/openssl/1.0.1e/include --libpath /usr/local/Cellar/openssl/1.0.1e/lib -j 8

Typical Debug Build
~~~~~~~~~~~~~~~~~~~

    bash ~/projects/willitlink/willitlink\_gen.sh --dd --mute -j 8

Operation
---------

These ingestion operations should create a file called
``dep_graph.json` in the ``~/projects/willitlink``, with a number of
other build artifacts.

The ``dep_graph.py`` file provides an interface for the data in
``dep_graph.json``.  See ``find_leaks.py`` for an example of how to
use this library.

Eventually ``wil.py`` will be the basis for all interaction with all
``willitlink`` tools and operations.
