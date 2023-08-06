import unittest
import os
from xalanih.core.sqlfileexecutor import SqlFileExecutor
from xalanih.test.mocks.logger import Logger
from xalanih.test.mocks.connection import Connection

class TestSqlFileExecutor(unittest.TestCase):

    def setUp(self):
        self.connection = Connection()
        self.logger = Logger()
        self.dir = os.path.dirname(__file__) + "/data/executor_test/"

    def tearDown(self):
        self.connection.reinit()

    def test_executeSuccess(self):
        sqlFile = open(self.dir + "success.sql")
        SqlFileExecutor.execute(self.connection, sqlFile, self.logger)
        sqlFile.close()
        self.assertEqual(len(self.connection.getQueries()), 3,
                            "Wrong number of request executed.")

    def test_executeEmpty(self):
        sqlFile = open(self.dir + "empty.sql")
        SqlFileExecutor.execute(self.connection, sqlFile, self.logger)
        sqlFile.close()
        self.assertEqual(len(self.connection.getQueries()), 0,
                            "Wrong number of request executed.")
