========================
``wil`` -- Will it link?
========================

Welcome to Willitlink!

This project is aimed to help manage the dependencies of large statically linked C and C++ projects.

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

What is static linking, and how does it affect my project?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two types of linking in a C and C++ project.

Static Linking
    Static Linking consists of compiling all source files, and building them all together into the
    resulting executable.  The advantage of this is that the executable can run on its own without
    any extra pieces, but the disadvantage is that this process can lead to large executables, and,
    since everything gets mashed together in the end, there is no built in mechanism to enforce any
    module structure.

Dynamic Linking
    Dynamic Linking is cool, but can also be a pain.  This consists of building the executable, but
    only with the core components.  The executable can then have "Shared Library" dependencies,
    rather than "Static Library" dependencies.  What this means is that at runtime the executable
    will load the libraries when it needs to, rather than having everything built into one giant
    blob and loaded at once.  The advantage to this is that the executable is smaller, and we have
    an enforced modular structure, but the disadvantage is you need to make sure that the executable
    can actually FIND the libraries it needs, and that they are the right version.

ASCII Art of Build Process, with terminology:

::

    Source Files:                            a.cpp    b.cpp    c.cpp
    Compile:                                  ||       ||       ||
                                              \/       \/       \/
    Object Files:                            a.o      b.o      c.o
    Create Library:                           ||       \\      //
                                              ||         \\  //
    Static Library (Shared Library):          ||         libbc.a (libbc.so)
    Linking:                                  \\         //
                                                \\      //
    Executable:                                   abc.exe

Note: I'll use the terms "Archive" and "Library" interchangeably.

What does this project actually show us?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project shows us what our dependencies are between things.  There are two types of dependencies
that we care about:

Symbol Dependency
    A dependency of an object file or library on a symbol (variable, function definition, class
    definition) that is found in another object file or library.

Build Dependency
    A dependency in the build of an object file or library on another object file or library.  We
    express this in a build system by making source files members an archive, or by adding archives
    as dependencies for other archives or executables.  Note that this is explicitly user defined,
    and how the build system actually builds the programs.  The build system does NOT have any
    information about the actual Symbol Dependencies (which is what can lead us to problems).

This project is primarily meant to help us find, and plug "Symbol Leaks":

Symbol Leak
    A Symbol Dependency of a library that is not found in the tree formed by all its Build
    Dependencies.  In practical terms, this means that the library cannot be used on its own without
    linking with something else that contains the necesary symbols.

A Symbol Leak can be of three types:

Simple Symbol Leak
    This is the case that is the easiest to fix.  It is the situation where the symbol needed by the
    library is contained in an library that can be added to the Build Dependencies of this library
    without any issues.

Circular Symbol Leak
    This is the case where the symbol needed by the library is contained in a library that
    eventually depends on this one.  This means we cannot add this library as a Build Dependency,
    since circular dependencies are not allowed in a build system.

Multiply Defined Symbol Leak
    This is the really messed up case.  It's a situation where the symbol needed by this library is
    defined in more than one place, so we don't even know which library to include (if we included
    more than one, we'd get a "duplicate definition" error).

Have fun!
