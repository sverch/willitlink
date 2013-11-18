========================
``wil`` -- Will it link?
========================

This is a proof of concept for the ``willitlink`` project.


Quick Start
-----------

::

   bash <path to repo>/willitlink\_gen.sh <scons flags>

   python wil.py leak-check libmongocommon.a 2

Build MongoDB with SSL
~~~~~~~~~~~~~~~~~~~~~~

::

   bash ~/projects/willitlink/willitlink\_gen.sh --ssl --dd --mute --cpppath /usr/local/Cellar/openssl/1.0.1e/include --libpath /usr/local/Cellar/openssl/1.0.1e/lib -j 8

Typical Debug Build
~~~~~~~~~~~~~~~~~~~

::

    bash ~/projects/willitlink/willitlink\_gen.sh --dd --mute -j 8

Operation
---------

These ingestion operations should create a file called ``dep_graph.json`` in the
``<willitlink>/data`` directory, with a number of other build artifacts.

The ``dep_graph.py`` file provides an interface for the data in ``dep_graph.json``.  See
``find_leaks.py`` for an example of how to use this library.

Eventually ``wil.py`` will be the basis for all interaction with all
``willitlink`` tools and operations.

Example of using wil.py to find symbols that libmongocommon.a is missing and are not included in any
libraries that libmongocommon.a declares as dependencies.  In the output here it is called a symbol
"leak":

::

    $ python wil.py leak-check libmongocommon.a 2
    [wil] [timer]: time elapsed for generating direct leak list was: 1.50856804848
    [
       {
          "leak": {
             "symbol": "mongo::inShutdown()",
             "file": "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/util/concurrency/task.o"
          },
          "sources": {
             "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/libserveronly.a": {
                "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/db/instance.o": {}
             },
             "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/client/scoped_db_conn_test.o": {},
             "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/s/server.o": {},
             "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/unittest/libunittest_crutch.a": {
                "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/unittest/crutch.o": {}
             },
             "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/libclientandshell.a": {
                "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/mongo/client/clientAndShell.o": {}
             },
             "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/client_build/libmongoclient.a": {
                "build/darwin/cpppath__usr_local_Cellar_openssl_1.0.1e_include/dd/libpath__usr_local_Cellar_openssl_1.0.1e_lib/ssl/client_build/mongo/client/clientAndShell.o": {}
             }
          }
       }
    ]

Next Version Specification
--------------------------

The following is a specification of the next version of the wil.py script.  Eventually the script
should follow this spec, with possible modifications, and this README can just have this section as
usage.

The arguments to wil.py will help determine the type of query being performed.  The usage and
various possible queries can be found below.

Basic Queries
~~~~~~~~~~~~~

Objects:

Get the archives that this object is a member of:

::

   $ python wil.py object archives sock.o
   {
       "contained_in" : [
           "build/darwin/normal/mongo/libnetwork.a",
           "build/darwin/normal/mongo/client_build/libmongoclient.a"
       ]
   }
   $

Get all symbol definitions for this object:

::

   $ python wil.py object symdefs sock.o
   {
       "defines" : [
           "mongo::Sock()",
           ...
       ]
   }
   $

Get all symbol dependencies for this object:

::

   $ python wil.py object symdeps sock.o
   {
       "requires" : [
           "mongo::verifyFailed()",
           ...
       ]
   }
   $

Get all basic info about this object:

::

   $ python wil.py object info sock.o
   {
       "contained_in" : [
           "build/darwin/normal/mongo/libnetwork.a",
           "build/darwin/normal/mongo/client_build/libmongoclient.a"
       ],
       "defines" : [
           "mongo::Sock()",
           ...
       ],
       "requires" : [
           "mongo::verifyFailed()",
           ...
       ]
   }
   $

Archives:

Get members of this archive:

::

   $ python wil.py archive objects libnetwork.a
   {
       "contains" : [
           "build/darwin/normal/mongo/util/net/sock.o",
           ...
       ]
   }
   $

Get all libraries that this library depends on:

::

   $ python wil.py archive libdeps libnetwork.a
   {
       "libdeps" : [
           "build/darwin/normal/mongo/libfoundation.a",
           ...
       ]
   }
   $

Get all libraries and executables that depend on this library:

::

   $ python wil.py archive uses libnetwork.a
   {
       "uses" : [
           "build/darwin/normal/mongo/libmongocommon.a",
           ...
       ]
   }
   $

Get all basic info about this object:

::

   $ python wil.py archive info libnetwork.a
   {
       "contains" : [
           "build/darwin/normal/mongo/util/net/sock.o",
           ...
       ],
       "libdeps" : [
           "build/darwin/normal/mongo/libfoundation.a",
           ...
       ],
       "uses" : [
           "build/darwin/normal/mongo/libmongocommon.a",
           ...
       ]
   }
   $

Symbols:

Get all places where this symbol is defined:

::

   $ python wil.py symbol definitions "mongo::Sock()"
   {
       "definitions" : [
           "build/darwin/normal/mongo/util/net/sock.o",
           ...
       ]
   }

Get all places where this symbol is needed:

::

   $ python wil.py symbol uses "mongo::Sock()"
   {
       "uses" : [
           "build/darwin/normal/mongo/util/net/listen.o",
           ...
       ]
   }

Get all basic info about this symbol:

::

   $ python wil.py symbol info "mongo::Sock()"
   {
       "definitions" : [
           "build/darwin/normal/mongo/util/net/sock.o",
           ...
       ],
       "uses" : [
           "build/darwin/normal/mongo/util/net/listen.o",
           ...
       ]
   }

All queries should optionally allow more than one filename or symbol name, which will result int the
hash being nested one layer deeper and keyed first on the name of with symbol file the stats are
related to.  Example:

Get all libraries and executables that depend on this library:

::

   $ python wil.py archive uses libnetwork.a libmongocommon.a
   {
       "build/darwin/normal/mongo/libnetwork.a" : {
           "uses" : [
               "build/darwin/normal/mongo/libmongocommon.a",
               ...
           ]
       },
       "build/darwin/normal/mongo/libmongocommon.a" : {
           "uses" : [
               "build/darwin/normal/mongo/libcoreserver.a",
               ...
           ]
       }
   }
   $

Complex Queries
~~~~~~~~~~~~~~~

The first complex query pattern will come from appending "-tree" to the end of the first argument to
any of the basic queries.  Any queries that have results involving the scons dependency tree will
print the complete family tree by default.  The last argument in this case will be interpreted as
the "depth".  Example:

Get all libraries and executables that depend on this library, and things that depend on each of
those dependencies, and so on up to a depth of 4:

::

   $ python wil.py archive-tree uses libnetwork.a 4
   {
       "uses": {
           // Top level is things that depend on libnetwork.a directly
           "build/darwin/normal/mongo/libmongocommon.a" : {
               // Things that depend on libmongocommon.a
               "build/darwin/normal/mongo/libcoreserver.a" : {
                   ...
               }
               ...
           },
           ...
       }
   }
   $

The next complex queries will answer more interesting questions about the objects in our build.  The
previous queries are good for traversing the dependency tree, but are missing information about the
overlap between build dependencies and symbol dependencies.

Libdeps:

Get extra libdeps for the given archive.  Note that this is determined by where symbols are needed
and used.

::

   $ python wil.py archive extra-libdeps libnetwork.a
   {
       "extra-libdeps": [
           "build/darwin/normal/mongo/libstringutils.a",
           ...
       ]
   }
   $

Get missing libdeps for the given archive.  Note that this is determined by where symbols are needed
and used.

::

   $ python wil.py archive missing-libdeps libnetwork.a
   {
       "missing-libdeps": [
           "build/darwin/normal/mongo/liblasterror.a",
           ...
       ]
   }
   $

Get all libdeps needed for the given list of files.  This uses symbol information for all the files
provided.  Useful for creating new libraries.  A nested array will be shown to indicate that one of
multiple libraries could be used (in the case where a symbol is defined in multiple places).

::

   $ python wil.py archive needed-libdeps libnetwork.a
   {
       "needed-libdeps": [
           "build/darwin/normal/mongo/libassertions.a",
           ...
       ]
   }
   $

Get all libdeps needed for the given list of files, and include information about why.  This uses
symbol information for all the files provided.  Useful for creating new libraries.  Note that the
"-tree" trick should also work here, since the "defined" section could include a family tree.

::

   $ python wil.py archive needed-libdeps-detail libnetwork.a
   {
       "needed-libdeps": [
           {
               "symbol" : "mongo::verifyFailed()",
               "used" : [ "build/darwin/normal/mongo/sock.o" ],
               "defined" : [{
                   "build/darwin/normal/mongo/libassertions.a" : {
                       "build/darwin/normal/mongo/util/verify.o" : {}
                   }
               }]
           }
       ]
   }
   $

Get information about how two files are related.  This includes the relationship of symbols as well
as the relationship in the build.  The question is "how is this first thing related to the second".

::

   $ python wil.py relationship libnetwork.a sock.o
   {
        "trees" : [{
            "mongo/build/darwin/normal/mongo/libnetwork.a": {
                "mongo/build/darwin/normal/mongo/util/net/sock.o": {}
            }
        }]
       "relationship" : "component", // Could be "child", "sibling", "parent", or "ambiguous"
       "symdefs" : [
          // Data about symbols used by sock.o defined in libnetwork.a.  Should follow the same
          // convention as the output for the symbol commands above.
       ],
       "symdeps" : [
          // Data about symbols used by libnetwork.a defined in sock.o.  Should follow the same
          // convention as the output for the symbol commands above.
       ]
   }
   $

Get the external interface to a collection of files.  These are symbols that are used from outside
the set of files provided.  Useful for determining the external interface to a library.

::

   $ python wil.py interface libnetwork.a sock.o
   {
       "symdefs" : [
          // Data about symbols used from outside sock.o and libnetwork.a that are defined in sock.o
          // and libnetwork.a.  Should follow the same convention as the output for the symbol
          // commands above.
       ]
   }
   $

For each of the file related commands, the special keyword "all" can be used to mean "all files".
Files that don't have relevant results will not be included in the output.  For example, to find all
libraries that don't include what they need, run:

::

   $ python wil.py archive missing-libdeps all
   {
       "build/darwin/normal/mongo/libnetwork.a" : {
           "missing-libdeps": [
               "build/darwin/normal/mongo/liblasterror.a",
               ...
           ]
       },
       ...
   }
   $
