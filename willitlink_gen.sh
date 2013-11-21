#!/bin/bash

# This file is glue holding a bunch of scripts together to generate the symbol and file dependencies
# for MongoDB

# You can pass build flags after the command to add them to the build.  Recommend building with SSL
# now to detect more dependencies.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python $DIR/wil.py collect -m `pwd` --tree_name $DIR/data/dependency_tree.txt --data $DIR/data/deps.json --scons $@

echo "[wil]: completed data generation, moving to ingestion phase."
python $DIR/wil.py ingest -t -m `pwd` --input_tree $DIR/data/dependency_tree.txt --dep_info $DIR/data/deps.json --output_dep_name $DIR/data/dep_graph.json 
