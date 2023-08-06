import os
import psycopg2
import unittest
from breezeblocks import Database

from base_dml_chinook_tests import BaseDMLChinookTests

DB_URL = "postgres://{user}:{password}@localhost:{port}/Chinook".format(
    user=os.getenv("PGUSER"), password=os.getenv("PGPASS"), port=os.getenv("PGPORT"))

class PostgresChinookDMLTests(BaseDMLChinookTests, unittest.TestCase):
    """DML tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        self.db = Database(dsn=DB_URL, dbapi_module=psycopg2)
