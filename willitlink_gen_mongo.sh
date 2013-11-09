#!/bin/bash

# This file is glue holding a bunch of scripts together to generate the symbol and file dependencies
# for MongoDB

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -f $DIR/deps.json

# Code to extract the build system dependencies that SCons knows about plus the symbol data in our
# object files.
# TODO: When I'm doing this in more of a sane way (like integrating with the build system) don't
# hard code what kind of build I'm doing.  Building with SSL now to detect more dependencies.

# Build to make sure we have all our .o files for willitlink.py
scons $@ all

# Prints out a "tree" of dependencies to the given file
rm -f $DIR/dependency_tree.txt
scons $@ --tree=all,prune all >> $DIR/dependency_tree.txt

# Script to parse the tree and insert json
# TODO: don't hard code the mongo port and collection in the script
python $DIR/parse_scons_dependency_tree.py $DIR/dependency_tree.txt

# Code to extract the dependencies between "*.a" files.  We need to do this because we have our own
# custom thing that handles LIBDEPS specially in site_scons/libdeps.py
git checkout site_scons/libdeps.py
git apply $DIR/print_scons_libdeps.patch
scons $@ all | grep -e "^{" >> $DIR/deps.json

# Finally, the script that actually imports the json files
# TODO: don't hard code the mongo port and collection in the script
python $DIR/import_dep_info.py $DIR/deps.json

# Now, do the work to clean up our symbols.  This eliminates symbols that aren't defined anywhere in
# our project, as they are not useful to know about and just cause noise (e.g. std::string and
# random linker symbols).
python $DIR/create_symbol_collections.py
