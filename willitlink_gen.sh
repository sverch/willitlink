#!/bin/bash

# This file is glue holding a bunch of scripts together to generate the symbol and file dependencies
# for MongoDB

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[wil]: cleanup previous artifacts"
rm -f $DIR/deps.json $DIR/dep_graph.json $DIR/dependency_tree.txt

# Code to extract the build system dependencies that SCons knows about plus the symbol data in our
# object files.

# TODO: When I'm doing this in more of a sane way (like integrating with the build system) don't
# hard code what kind of build I'm doing. Building with SSL now to detect more dependencies.

# Build to make sure we have all our .o files for willitlink.py
scons -Q --silent --ssl $@ all

# Prints out a "tree" of dependencies to the given file
scons --ssl $@ --tree=all,prune all >> $DIR/dependency_tree.txt

# Code to extract the dependencies between "*.a" files.  We need to do this because we have our own
# custom thing that handles LIBDEPS specially in site_scons/libdeps.py
git checkout site_scons/libdeps.py
git apply $DIR/print_scons_libdeps.patch
scons --ssl $@ all | grep -e "^{" >> $DIR/deps.json
git checkout site_scons/libdeps.py

echo "[wil]: completed data generation, moving to ingestion phase."
python $DIR/new_ingestion.py -t $DIR/dependency_tree.txt $DIR/deps.json $DIR/dep_graph.json
