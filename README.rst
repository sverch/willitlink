========================
``wil`` -- Will it link?
========================

Welcome to Willitlink!

This project aims to help manage the dependencies of large statically linked C
and C++ projects. In particular, it's designed to help new projects avoid, and
existing projects reduce, the number of unintended or misunderstood circular
dependencies between source files.

Quick Start
-----------

Collect the data from scons (does a full build).  Note the quote around the scons flags.  deps.json and dependency_tree.txt are intermediate files to be used in the next command.

::

   python wil.py collect -m <path_to_mongodb_repo> --scons "<scons_flags>"

Complete the initial data processing and make the result dataset.

::

   python wil.py ingest -t -m <path_to_mongodb_repo>

Example Queries
~~~~~~~~~~~~~~~

Get all symbols needed by this archive that are not defined by this archive or anything it depends on (meaning that this archive will not link on its own).

::

    python wil.py tree --leak libmongocommon.a

Get all symbols needed by this archive that are not defined by this archive or anything it depends on (meaning that this archive will not link on its own) AND are also not defined in the files provided after the "-s".  This is a way to get rid of unnecessary noise (symbols that you know are leaking but don't want to look at).

::

    python wil.py tree --leak libmongocommon.a -s unittest/crutch.o

Get the interface of a set of files

::

    python wil.py interface libmongocommon.a sock.o

Get all libraries needed by this archive.  The "bad" entry in the dictionary represents a symbol that is defined in more than one place, which means that "one of these archives" is needed to link.

::

    python wil.py libs-needed libmongocommon.a

Get circular dependencies for the library.

::

    python wil.py libs-cycle liblasterror.a

Project Motivation
------------------

In one phrase, the motivation of this project is to help people with statically
linked projects get out of dependency hell.

Poorly understood dependencies can have a big impact on the ability of
engineers to get up to speed on a project.  As more circular dependencies accrue
on a codebase, it becomes more and more difficult for anyone to have confidence
in what the code seems to be doing.  A state change or key behavior could appear
anywhere along the dependency chain.  Without tracing that whole chain from
start to finish, an engineer may not be able to confirm that things happen the
way they expect.

Poorly understood dependencies also make it more difficult to test features.
When you write a unit test, in the ideal case you would only build the library
being unittested, plus its dependencies. That way if it breaks, you have a much
smaller search-space to find the problem. But if the dependencies between
libraries aren't well-defined, they may end up including the whole code base.
That means if the test fails for any reason, the debugging process could involve
every file in the code base, for what was meant to be an isolated component
test.

How do these dependencies happen? The reason is that a dependency can be hard to
see. You could try to figure out what modules are in a large project by looking
at the directory structure, only to discover that the actual division of modules
is very different. A statically linked program may compile and link
successfully, even if the chain of dependencies eliminate all meaningful
separations between the parts of the project.

Willitlink is a script that identifies the dependencies between files, so that
engineers can see what they are and make informed decisions about what they
should be.  In a well defined modular code base, the barrier to entry can be
understanding one module rather than understanding every part of the project.

Once a codebase has well structured dependencies, Willitlink can be automated to
enforce the desired structure as a compile time check, and it can also be used
to reveal what symbols are actually used in a library.

Because willitlink uses the real up-to-date data from the build, it provides a
source of truth that can't be found by looking at the directory hierarchy or the
libraries created by the build system.

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
