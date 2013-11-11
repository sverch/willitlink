This is a proof of concept for the willitlink project

# Quick start:

    bash <path to repo>/willitlink\_gen.sh <scons flags>

# Examples:

My SSL build:

    bash ~/projects/willitlink/willitlink\_gen.sh --ssl --dd --mute --cpppath /usr/local/Cellar/openssl/1.0.1e/include --libpath /usr/local/Cellar/openssl/1.0.1e/lib -j 8

My normal debug build:

    bash ~/projects/willitlink/willitlink\_gen.sh --dd --mute -j 8

This should populate the ~/projects/willitlink directory with a file called dep\_graph.json.  This
is a file in a format that is readable by the graph library in dep\_graph.py.  See find\_leaks.py
for an example of how to use this library.
