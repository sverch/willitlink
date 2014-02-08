# Project Browser

## Files

### External Use
* process\_project\_data.py - API to add willitlink data and get the final processed version of the data.  Entry point for the system

### Internal Files
* data\_access.py - All access to data files should be here.  Look at this to find the expected locations of different parts of the data
* get\_willitlink\_data.py - Helpers to read and add willitlink data to a human generated modules object

### Other Helpers
* diff\_project\_files.py - Standalone script to diff the current version of a human generated modules file with the corresponding willitlink data
* readme\_generator.py - Standalone script to generate a tree of README.md files from the data for browsing on github
