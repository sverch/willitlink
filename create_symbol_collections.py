#!/usr/bin/env python

import re
import json
import pymongo
import subprocess
import sys
client = pymongo.MongoClient()

# The purpose of this file is to "prune" the data so that we only have symbols that are defined or
# used somewhere in our project this may not be necessary when we have our new "edges dictionaries"
# data format.

def insertCleanedBuildObject(buildObject):
    try:
        client['test'].deps_cleaned.insert(buildObject)
    except pymongo.errors.DuplicateKeyError:
        print("Duplicate Key!")

symbol_dependency_set = set()
def insertSymbolDependency(symbol):
    if symbol not in symbol_dependency_set:
        symbol_dependency_set.add(symbol)
        try:
            client['test'].symbol_dependency.insert({ "name" : symbol })
        except pymongo.errors.DuplicateKeyError:
            print("Duplicate Key!")

symbol_definition_set = set()
def insertSymbolDefinition(symbol):
    if symbol not in symbol_definition_set:
        symbol_definition_set.add(symbol)
        try:
            client['test'].symbol_definition.insert({ "name" : symbol })
        except pymongo.errors.DuplicateKeyError:
            print("Duplicate Key!")


symbol_dependency_extra_set = set()
def insertSymbolDependencyExtra(symbol):
    symbol_dependency_extra_set.add(symbol)
    try:
        client['test'].symbol_dependency_extra.insert({ "name" : symbol })
    except pymongo.errors.DuplicateKeyError:
        print("Duplicate Key!")

symbol_definition_extra_set = set()
def insertSymbolDefinitionExtra(symbol):
    symbol_definition_extra_set.add(symbol)
    try:
        client['test'].symbol_definition_extra.insert({ "name" : symbol })
    except pymongo.errors.DuplicateKeyError:
        print("Duplicate Key!")

symbol_dependency_core_set = set()
def insertSymbolDependencyCore(symbol):
    symbol_dependency_core_set.add(symbol)
    try:
        client['test'].symbol_dependency_core.insert({ "name" : symbol })
    except pymongo.errors.DuplicateKeyError:
        print("Duplicate Key!")

symbol_definition_core_set = set()
def insertSymbolDefinitionCore(symbol):
    symbol_definition_core_set.add(symbol)
    try:
        client['test'].symbol_definition_core.insert({ "name" : symbol })
    except pymongo.errors.DuplicateKeyError:
        print("Duplicate Key!")

def extractSymDeps():
    for buildObject in client['test'].deps.find():
        if buildObject['type'] == 'object':
            if 'symdeps' in buildObject:
                for symdep in buildObject['symdeps']:
                    insertSymbolDependency(symdep)
            if 'symdefs' in buildObject:
                for symdef in buildObject['symdefs']:
                    insertSymbolDefinition(symdef)

def extractExtraSymDeps():
    for symbol_dependency in client['test'].symbol_dependency.find():
        #if client['test'].symbol_definition.find({ 'name' : symbol_dependency['name'] }).count() == 0:
        if symbol_dependency['name'] not in symbol_definition_set:
            insertSymbolDependencyExtra(symbol_dependency['name'])
        else:
            insertSymbolDependencyCore(symbol_dependency['name'])

    for symbol_definition in client['test'].symbol_definition.find():
        #if client['test'].symbol_dependency.find({ 'name' : symbol_definition['name'] }).count() == 0:
        if symbol_definition['name'] not in symbol_dependency_set:
            insertSymbolDefinitionExtra(symbol_definition['name'])
        else:
            insertSymbolDefinitionCore(symbol_definition['name'])

def removeExtraSymDeps():
    #dependencies = list(client['test'].symbol_dependency_core.find())
    #definitions = list(client['test'].symbol_definition_core.find())
    for buildObject in client['test'].deps.find():
        if buildObject['type'] == 'object':
            new_symdeps = []
            new_symdefs = []
            if 'symdeps' in buildObject:
                for symdep in buildObject['symdeps']:
                    # Only add it if it is defined somewhere in the project
                    for project_dep in symbol_dependency_core_set:
                        if symdep == project_dep:
                            new_symdeps += [ symdep ]

            if 'symdefs' in buildObject:
                for symdef in buildObject['symdefs']:
                    # Only add it if it is used somewhere in the project
                    for project_def in symbol_definition_core_set:
                        if symdef == project_def:
                            new_symdefs += [ symdef ]

            buildObject["symdeps"] = new_symdeps
            buildObject["symdefs"] = new_symdefs
            insertCleanedBuildObject(buildObject)
        else:
            insertCleanedBuildObject(buildObject)

def main():
    extractSymDeps()
    extractExtraSymDeps()
    removeExtraSymDeps()

main()
