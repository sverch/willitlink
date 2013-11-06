#!/usr/bin/env python

import re
import json
import pymongo
import subprocess
import sys
client = pymongo.MongoClient()

# Phase 1: Parsing the --tree=all output of scons
#
# Theory: The file is too big to put in a single dictionary, so we have to output JSON documents as
# they come.  Each recursive call outputs a JSON document before it returns, since it knows the sub
# elements.
# TODO: Automatically remove the empty string that sneaks in
# TODO: Remove /bin/ar and /bin/ranlib from the file dependencies for the archives

symbol_set = set()
def insertBuildElement(buildElement):
    if buildElement['_id'] not in symbol_set:
        symbol_set.add(buildElement['_id'])
        #print json.dumps(buildElement)
        try:
            client['test'].deps.insert(buildElement)
        except pymongo.errors.DuplicateKeyError:
            print "Duplicate Key!"

def detectType(line):
    if re.search(".*\.h", line):
        return "header"

    if re.search(".*\.o", line):
        return "object"

    if re.search(".*\.a", line):
        return "archive"

    if re.search(".*\.js", line):
        return "javascript"

    # Assume it's a system file if it starts with a '/'
    if re.search("^\/", line):
        return "system"

    return "target"

def getSymUses(objfile):
    uses = subprocess.check_output("nm -u " + objfile + " | c++filt", shell=True)
    uses = uses.split('\n')
    return uses

def getSymDefinitions(objfile):
    definitions = subprocess.check_output("nm -jU " + objfile + " | c++filt", shell=True)
    definitions = definitions.split('\n')
    return definitions

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
def parseTreeRecursive(fileHandle, depth, name, typeName, results):
    currentBuildElement = {}
    currentBuildElement['_id'] = name
    currentBuildElement['type'] = typeName

    prefix = ""

    for i in range(0, depth):
        prefix += "."

    for line in fileHandle:

        # TODO: handle that weird case here (with the code inline)
        # Weeeeird......
        if re.search("\+-[ ]*$", line) != None:
            # This is pretty awful
            inlineCodeString = ""
            for line in fileHandle:
                if re.search("\+-", line) != None:
                    break
                inlineCodeString = inlineCodeString + line
            currentBuildElement['inlineCode'] = inlineCodeString

        # If we see something at our prefix, we know we've reached the end of this section
        if re.search("^" + prefix + "\+-", line) != None:
            #results += [ currentBuildElement ]
            insertBuildElement(currentBuildElement)
            return line

        # If we see something below our prefix, we have an element to add (and maybe a section)
        elif re.search(prefix + "..\+-(.+)", line) != None:
            m = re.search(prefix + "..\+-\[(.+)\]", line)
            if m == None:
                m = re.search(prefix + "..\+-(.+)", line)
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
                        currentBuildElement['symdeps'] = getSymUses(name)
                    if 'symdefs' not in currentBuildElement:
                        currentBuildElement['symdefs'] = getSymDefinitions(name)
                elif typeName == "archive":
                    if 'objects' not in currentBuildElement:
                        currentBuildElement['objects'] = []
                    currentBuildElement['objects'] = currentBuildElement['objects'] + [ nextSection ]
                    nextSectionTypeName = "object"
                else:
                    if 'deps' not in currentBuildElement:
                        currentBuildElement['deps'] = []
                    currentBuildElement['deps'] = currentBuildElement['deps'] + [ nextSection ]
                    nextSectionTypeName = detectType(nextSection)

                # Parse any lines that are a level deeper than where we are now (may be none, which
                # would correspond to an object with no dependencies)
                lineAfterSection = parseTreeRecursive(fileHandle, depth + 2, nextSection, nextSectionTypeName, results)

                # Figure out why we exited.  Either it's because we are still in the same section,
                # or we are done with THIS section too and should exit.
                if lineAfterSection == None:
                    # EOF
                    #results += [ currentBuildElement ]
                    insertBuildElement(currentBuildElement)
                    return lineAfterSection
                elif re.search("^" + prefix + "..\+-", lineAfterSection) != None:
                    m = re.search(prefix + "..\+-\[(.+)\]", lineAfterSection)
                    if m == None:
                        m = re.search(prefix + "..\+-(.+)", lineAfterSection)
                    nextSection = m.group(1)
                else:
                    #results += [ currentBuildElement ]
                    insertBuildElement(currentBuildElement)
                    return lineAfterSection
        else:
            #results += [ currentBuildElement ]
            insertBuildElement(currentBuildElement)
            return line

def parseTree(filename):
    treeFile = open(filename, 'r')

    # First skip all our garbage lines not related to the tree output
    for line in treeFile:
        if re.search("^\+-all$", line) != None:
            break

    m = re.search("^\+-(.*)$", line)
    baseSection = m.group(1)

    # Start parsing our tree, starting with the base group
    results = []
    parseTreeRecursive(treeFile, 0, baseSection, "target", results)
    return results

def main():
    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " <depsfile>"
        sys.exit(1)

    filename = sys.argv[1]
    #if re.search(".*\.h", buildElement['_id']) is None:
    parseTree(filename)
    #for buildElement in parseTree(filename):
        #print json.dumps(buildElement)

main()
