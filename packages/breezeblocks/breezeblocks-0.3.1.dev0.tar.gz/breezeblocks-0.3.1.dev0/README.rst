BreezeBlocks
============

.. image:: https://readthedocs.org/projects/breezeblocks/badge/?version=latest
   :target: http://breezeblocks.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

BreezeBlocks is a lightweigt SQL abstraction layer that seeks to allow users
to interact with their database as a relational store. The user constructs
Python objects which represent the structure of the database, but these are
then used to build SQL statements and do not also represent records.

In other words, BreezeBlocks attempts to avoid or delay, depending on how
you see it, establishing an object-relation mapping. Eventually any query
result will need to be instantiated as a Python object in the
`isinstance(o, object)` sense, but not always in the class-based object-
oriented sense. BreezeBlocks does use Python classes, but by not making
a 1:1 correspondence of database tables to classes it can allow for more
natural use of the other paradigms Python provides.

BreezeBlocks is designed as a statement builder rather than an ORM.
SQL Syntax is exposed in Python classes which are passed into methods for
query construction. Query results are plain-old-data types similar to a C
struct. They provide access to fields of the row by name, but are still
compact and don't have as much usage overhead as most Python objects.

The contrasting approach is an ORM implementing something similar to
the Active Record pattern. A class is defined for each table,  with class-level
properties representing the columns. Rows in the table become instances of
their class.

This package is meant to help you use databases, not manage databases.
Querying, inserting, updating, and deleting (row-level operations) are within
scope of the project. Creating tables, views, and triggers is not.
