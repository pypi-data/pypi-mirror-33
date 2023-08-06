import os
import sqlite3
import unittest
from breezeblocks import Database

from base_query_chinook_tests import BaseQueryChinookTests

DB_URL = os.path.join(os.path.dirname(__file__), "Chinook.sqlite")

class SQLiteChinookQueryTests(BaseQueryChinookTests, unittest.TestCase):
    """Tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        self.db = Database(dsn=DB_URL, dbapi_module=sqlite3)
    
    @unittest.skip("NULLS { FIRST | LAST } syntax not supported by SQLite currently.")
    def test_orderByNullsFirst(self):
        pass
    
    @unittest.skip("NULLS { FIRST | LAST } syntax not supported by SQLite currently.")
    def test_orderByNullsLast(self):
        pass
    
    @unittest.skip("Right Outer Join not supported by SQLite currently.")
    def test_rightOuterJoin(self):
        pass
    
    @unittest.skip("Full Outer Join not supported by SQLite currently.")
    def test_fullOuterJoin(self):
        pass
