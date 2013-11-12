#!/bin/bash

# This file is glue holding a bunch of scripts together to generate the symbol and file dependencies
# for MongoDB

# You can pass build flags after the command to add them to the build.  Recommend building with SSL
# now to detect more dependencies.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[wil]: cleanup previous artifacts"
rm -f $DIR/deps.json $DIR/dep_graph.json $DIR/dependency_tree.txt

# Build to make sure we have all our .o files for willitlink.py
# Also includes special code to extract the dependencies between "*.a" files.
# We need to do this because we have our own
# custom thing that handles LIBDEPS specially in site_scons/libdeps.py

git checkout SConstruct
git checkout site_scons/libdeps.py
git apply $DIR/print_scons_libdeps.patch
scons $@ all | grep -e "^{" >| $DIR/deps.json
git checkout site_scons/libdeps.py

# Prints out a "tree" of dependencies to the given file
scons $@ --tree=all,prune all >| $DIR/dependency_tree.txt

echo "[wil]: completed data generation, moving to ingestion phase."
python $DIR/wil.py ingest -t $DIR/dependency_tree.txt $DIR/deps.json $DIR/dep_graph.json
