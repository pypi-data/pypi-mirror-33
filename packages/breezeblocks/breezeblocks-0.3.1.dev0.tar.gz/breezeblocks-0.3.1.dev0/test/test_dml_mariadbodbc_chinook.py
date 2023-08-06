import os
import pyodbc
import unittest
from breezeblocks import Database

from base_dml_chinook_tests import BaseDMLChinookTests

CONNECTION_STRING = "Driver=MariaDB;User ID={};Password={};Data Source=127.0.0.1;Database=chinook".format(
    os.getenv("MARIADBUSER"), os.getenv("MARIADBPASS"))

class MariaDBODBCTests(BaseDMLChinookTests, unittest.TestCase):
    """Tests using MariaDB through an ODBC adapter."""
    
    def setUp(self):
        self.db = Database(dsn=CONNECTION_STRING, dbapi_module=pyodbc)
