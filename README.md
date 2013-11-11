This is a proof of concept for the willitlink project

# Files to generate the data set:
Script to tie it all together:
willitlink\_gen.sh

Script to parse and import dependency tree from scons:
parse\_scons\_dependency\_tree.py

Script and patch to extract Library dependencies (which SCons does not know about):
import\_dep\_info.py
print\_scons\_libdeps.patch
