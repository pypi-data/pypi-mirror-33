Desctiption
-----------

Common code shared among in-house Bioinformatics python packages, such as:

- Parsing of FastQC output
- Manipulating FASTA sequences
- Building and using database of conversion GeneBank id (gi) to scientific name

Python version
--------------

This project is currently using Python 2.7

Installation
------------

It is recommended to use **virtualenv** to create a clean python environment.

To install bioutils, use **pip**:

    pip install bbcu.bioutils

Testing
-------
To run unit tests, use:

    nosetests

Or:

    tox

This suite includes both unit and more time-consuming integration tests


Execution
---------

The main script shipped with this project is **gi2name.py**, see its options by running:

The database is built by the script: **build-taxonomy-db.py**

