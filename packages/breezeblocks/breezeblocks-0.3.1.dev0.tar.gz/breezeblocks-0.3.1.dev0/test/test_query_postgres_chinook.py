import os
import psycopg2
import unittest
from breezeblocks import Database

from base_query_chinook_tests import BaseQueryChinookTests

DB_URL = "postgres://{user}:{password}@localhost:{port}/Chinook".format(
    user=os.getenv("PGUSER"), password=os.getenv("PGPASS"), port=os.getenv("PGPORT"))

class PostgresChinookQueryTests(BaseQueryChinookTests, unittest.TestCase):
    """Tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        self.db = Database(dsn=DB_URL, dbapi_module=psycopg2)
    
    @unittest.skip("Postgres seems to sort string case-insensitively. Python does not.")
    def test_orderByAsc(self):
        pass
    
    @unittest.skip("Postgres seems to sort string case-insensitively. Python does not.")
    def test_orderByDesc(self):
        pass
