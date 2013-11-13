=========================================
Overview of the MultiGraph Data Structure
=========================================

The following document provides an overview of the data in the
graph structure. Use the methods provided by the ``MultiGraph()`` class to access
items in the data structure.

::

   {
      "symbols" : [
          "mongo::inShutdown()",
          ...
      ],
      "files" : [
          "src/mongo/db/shutdown.o",
          ...
      ],
      "symbol_to_file_sources" : {
           "mongo::inShutdown()" : [
               "shutdown.o",
           ],
           ...
      }
      "symbol_to_file_dependencies" : {
           "mongo::inShutdown()" : [
               "file_that_uses_shutdown.o",
           ],
           ...
      }
      "file_to_symbol_definitions" : {
           "shutdown.o" : [
               "mongo::inShutdown()",
           ],
           ...
      }
      "file_to_symbol_dependencies" : {
           "file_that_uses_shutdown.o" : [
               "mongo::inShutdown()",
           ],
           ...
      }
      "target_to_dependencies" : {
           "libshutdown.a" : [
               "libstringutils.a",
           ],
           "all" : [
               "alltools",
           ],
           ...
      }
      "archives_to_components" : {
           "libshutdown.a" : [
               "shutdown.o",
           ],
           ...
      }
      "dependency_to_targets" : {
           "shutdown.o" : [
               "libshutdown.a",
           ],
           "libstringutils.a" : [
               "libshutdown.a"
           ],
           ...
      }
   }
