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
