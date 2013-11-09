#!/usr/bin/env python

import re
import json
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import subprocess
import sys
import extract_symbols

# Phase 1: Parsing the --tree=all output of scons
#
# Theory: The file is too big to put in a single dictionary, so we have to output JSON documents as
# they come.  Each recursive call outputs a JSON document before it returns, since it knows the sub
# elements.
# TODO: Automatically remove the empty string that sneaks in
# TODO: Remove /bin/ar and /bin/ranlib from the file dependencies for the archives

symbol_set = set()
def persist_node(buildElement, results):
    if buildElement['_id'] not in symbol_set:
        symbol_set.add(buildElement['_id'])

        if isinstance(results, MongoClient):
            try:
                results['test'].deps.insert(buildElement)
            except DuplicateKeyError:
                print("Duplicate Key!")
        elif isinstance(results, list):
            results.append(buildElement)
        else:
            print('not persisting {0}'.format(buildElement['_id']))

def detect_type(line):
    if line.endswith('.h'):
        return "header"

    if line.endswith('.o'):
        return "object"

    if line.endswith('.a'):
        return "archive"

    if line.endswith('.js'):
        return "javascript"

    # Assume it's a system file if it starts with a '/'
    if line.startswith('/'):
        return "system"

    return "target"

# Arguments:
# fileHandle - File we are iterating
# depth - depth of this section
# name - name of this section
#
# Returns:
# sectionName - The name of the next section (because we have to read that line to know when to
# terminate)
#
# Prints:
# The current object with deps

class RegexLib(object):
    def __init__(self, depth):

        prefix = depth * '.'

        self.one = re.compile("\+-[ ]*$")
        self.two = re.compile("\+-")
        self.three = re.compile("^" + prefix + "\+-")
        self.four = re.compile(prefix + "..\+-(.+)")
        self.five = re.compile(prefix + "..\+-\[(.+)\]")
        self.six = re.compile(prefix + "..\+-(.+)")
        self.seven = re.compile("^" + prefix + "..\+-")

def recursive_parse_tree(fileHandle, depth, name, typeName, results):
    currentBuildElement = {
        '_id': name,
        'type': typeName
    }

    r = RegexLib(depth)

    for line in fileHandle:
        # TODO: handle that weird case here (with the code inline)
        # Weeeeird......
        if r.one.search(line) is not None:
            # This is pretty awful
            inline_code_string_parts = []
            for line in fileHandle:
                if r.two.search(line) is not None:
                    break
                inline_code_string_parts.append(line)
            currentBuildElement['inlineCode'] = ''.join(inline_code_string_parts)

        # If we see something at our prefix, we know we've reached the end of this section
        if r.three.search(line) is not None:
            persist_node(currentBuildElement, results)
            return line

        # If we see something below our prefix, we have an element to add (and maybe a section)
        elif r.four.search(line) is not None:
            m = r.five.search(line)
            if m == None:
                m = r.four.search(line)

            nextSection = m.group(1)

            while nextSection is not None:
                nextSectionTypeName = "target"

                # Based the type of file that we are currently parsing the dependencies for, name
                # the different kinds of dependencies.
                if typeName == "object":
                    # If this is a .o file then the first file afterwards is a source file, and the
                    # rest are headers.  Kind of a hack but we want to do it to avoid the issue with
                    # different file extensions.
                    if 'source' not in currentBuildElement:
                        currentBuildElement['source'] = nextSection
                        nextSectionTypeName = "source"
                    else:
                        if 'headers' not in currentBuildElement:
                            currentBuildElement['headers'] = []
                        currentBuildElement['headers'] = currentBuildElement['headers'] + [ nextSection ]
                        nextSectionTypeName = "header"

                    # Add our symbols!
                    if 'symdeps' not in currentBuildElement:
                        currentBuildElement['symdeps'] = extract_symbols.get_symbols_used(name)
                    if 'symdefs' not in currentBuildElement:
                        currentBuildElement['symdefs'] = extract_symbols.get_symbols_defined(name)
                elif typeName == "archive":
                    if 'objects' not in currentBuildElement:
                        currentBuildElement['objects'] = []
                    currentBuildElement['objects'] = currentBuildElement['objects'] + [ nextSection ]
                    nextSectionTypeName = "object"
                else:
                    if 'deps' not in currentBuildElement:
                        currentBuildElement['deps'] = []
                    currentBuildElement['deps'] = currentBuildElement['deps'] + [ nextSection ]
                    nextSectionTypeName = detect_type(nextSection)

                # Parse any lines that are a level deeper than where we are now (may be none, which
                # would correspond to an object with no dependencies)
                lineAfterSection = recursive_parse_tree(fileHandle, depth + 2, nextSection, nextSectionTypeName, results)

                # Figure out why we exited.  Either it's because we are still in the same section,
                # or we are done with THIS section too and should exit.
                if lineAfterSection is None:
                    # EOF
                    persist_node(currentBuildElement, results)
                    return lineAfterSection
                elif r.seven.search(lineAfterSection) is not None:
                    m = r.five.search(lineAfterSection)
                    if m is None:
                        m = r.six.search(lineAfterSection)
                    nextSection = m.group(1)
                else:
                    persist_node(currentBuildElement, results)
                    return lineAfterSection
        else:
            persist_node(currentBuildElement, results)
            return line

def parse_tree(filename, results):
    """
    Pass a filename of SCons tree output to parse.

    The results argument is either a list that parse_tree will return, or a
    pymongo.MongoClient object.
    """

    all_re = re.compile("^\+-all$")

    with open(filename, 'r') as treeFile:
        # First skip all our garbage lines not related to the tree output
        for line in treeFile:
            if all_re.search(line) is not None:
                break

        m = re.search("^\+-(.*)$", line)
        baseSection = m.group(1)

        # Start parsing our tree, starting with the base group
        recursive_parse_tree(treeFile, 0, baseSection, "target", results)

    if isinstance(results, list):
        return results
    elif isinstance(results, MongoClient):
        return True
    else:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <depsfile>")
        sys.exit(1)

    parse_tree(filename=sys.argv[1],
               results=MongoClient())

if __name__ == '__main__':
    main()
