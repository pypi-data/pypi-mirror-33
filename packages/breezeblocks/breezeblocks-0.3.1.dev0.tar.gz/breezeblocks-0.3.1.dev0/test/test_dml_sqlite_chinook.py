import os
import sqlite3
import unittest
from breezeblocks import Database

from base_dml_chinook_tests import BaseDMLChinookTests

DB_URL = os.path.join(os.path.dirname(__file__), "Chinook.sqlite")

class SQLiteChinookDMLTests(BaseDMLChinookTests, unittest.TestCase):
    """DML tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        self.db = Database(dsn=DB_URL, dbapi_module=sqlite3)
