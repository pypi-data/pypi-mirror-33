import unittest
import os
from xalanih.core.dbupdator import DBUpdator
from xalanih.core.constants import Constants
from xalanih.core.xalanihexception import XalanihException
from xalanih.core.mysql.mysqlrequesthandler import MysqlRequestHandler
from xalanih.test.mocks.connection import Connection
from xalanih.test.mocks.logger import Logger

class TestDBUpdatorMySQL(unittest.TestCase):

    def setUp(self):
        self.connection = Connection()
        self.logger = Logger()
        self.dir = os.path.dirname(__file__) + "/data/"
        self.req_handler = MysqlRequestHandler()
        self.dbupdator = DBUpdator(self.dir, self.connection, self.req_handler,
                                    self.logger)

    def tearDown(self):
        self.connection.reinit()
        self.dbupdator = None

    def test_applyUpdatesNoTable(self):
        self.connection.setResultList([()])
        with self.assertRaises(XalanihException) as cm:
            self.dbupdator.applyUpdates(None)
        self.assertEqual(cm.exception.getErrorCode(),
                            XalanihException.TABLE_NOT_FOUND,
                            "Wrong error code.")

    def test_applyUpdatesNoUpdates(self):
        self.connection.setResultList([((Constants.XALANIH_TABLE,),)])
        self.dir += "creation_test"
        self.dbupdator = DBUpdator(self.dir, self.connection, self.req_handler,
                                    self.logger)
        self.dbupdator.applyUpdates(None)
        queries = self.connection.getQueries()
        self.assertEqual(len(queries), 1)

    def test_applyUpdatesSuccess(self):
        self.dir += "update_test"
        inc_updates = self.getListofIncludedUpdates()
        updates = self.getListOfUpdates()

        self.connection.setResultList([((Constants.XALANIH_TABLE,),)])
        self.connection.setRowcountList(
                        [(1 if i <= len(inc_updates) else 0) for i in range(5)])
        self.dbupdator = DBUpdator(self.dir, self.connection, self.req_handler,
                                    self.logger)
        self.dbupdator.applyUpdates(None)

        queries = self.connection.getQueries()
        expectedQueries = 1 + len(updates) + 2*(len(updates)-len(inc_updates))
        self.assertEqual(len(queries), expectedQueries,
                            "Not the expected number of queries")

        for update in inc_updates:
            self.assertEqual(self.getNbRequested(queries, update), 1,
                                "Wrong amount of request linked to" 
                                " the included update: {0}".format(update))
        
        for update in [u for u in updates if u not in inc_updates]:
            self.assertEqual(self.getNbRequested(queries, update), 2,
                                "Wrong amount of request linked to" 
                                " the update: {0}".format(update))

    def test_applyUpdatesLastUpdateSuccess(self):
        self.dir += "update_test"
        inc_updates = self.getListofIncludedUpdates()
        updates = self.getListOfUpdates()
        last_update = updates[-2]

        self.connection.setResultList([((Constants.XALANIH_TABLE,),)])
        self.connection.setRowcountList(
                        [(1 if i <= len(inc_updates) else 0) for i in range(5)])
        self.dbupdator = DBUpdator(self.dir, self.connection, self.req_handler,
                                    self.logger)
        self.dbupdator.applyUpdates(last_update)

        queries = self.connection.getQueries()
        expectedQueries = 1 + (len(updates)-1) + 2*(len(updates)-len(inc_updates)-1)
        self.assertEqual(len(queries), expectedQueries,
                            "Not the expected number of queries")

        for update in inc_updates:
            self.assertEqual(self.getNbRequested(queries, update), 1,
                                "Wrong amount of request linked to" 
                                " the included update: {0}".format(update))
        
        for update in [u for u in updates 
                            if u not in inc_updates and u <= last_update]:
            self.assertEqual(self.getNbRequested(queries, update), 2,
                                "Wrong amount of request linked to" 
                                " the update: {0}".format(update))

    def test_applyUpdatesLastUpdateNotExist(self):
        self.dir += "update_test"
        inc_updates = self.getListofIncludedUpdates()
        updates = self.getListOfUpdates()
        last_update = "INVALID_UPDATE"
        self.connection.setResultList([((Constants.XALANIH_TABLE,),)])
        self.dbupdator = DBUpdator(self.dir, self.connection, self.req_handler,
                                    self.logger)
        with self.assertRaises(XalanihException) as cm:
            self.dbupdator.applyUpdates(last_update)
        self.assertEqual(cm.exception.getErrorCode(),
                            XalanihException.UPDATE_NOT_FOUND,
                            "Wrong error code.")


    def test_applyUpdatesLastUpdateInIncluded(self):
        self.dir += "update_test"
        inc_updates = self.getListofIncludedUpdates()
        updates = self.getListOfUpdates()
        last_update = inc_updates[0]

        self.connection.setResultList([((Constants.XALANIH_TABLE,),)])
        self.connection.setRowcountList(
                        [(1 if i <= len(inc_updates) else 0) for i in range(5)])
        self.dbupdator = DBUpdator(self.dir, self.connection, self.req_handler,
                                    self.logger)
        self.dbupdator.applyUpdates(last_update)

        queries = self.connection.getQueries()
        self.assertEqual(len(queries), 2,
                            "Not the expected number of queries")

        self.assertEqual(self.getNbRequested(queries, last_update), 1,
                            "Wrong amount of request linked to" 
                            " the included update: {0}".format(last_update))
        
        for update in [u for u in updates if u != last_update]:
            self.assertEqual(self.getNbRequested(queries, update), 0,
                                "Wrong amount of request linked to" 
                                " the update: {0}".format(update))




    def getListOfUpdates(self):
        directory = self.dir + "/" + Constants.DIR_UPDATE
        files = os.listdir(directory)
        res = [f[:-4] for f in files if f.endswith(".sql")]
        res.sort()
        return res

    def getListofIncludedUpdates(self):
        incfile = open(self.dir + "/" + Constants.PATH_INC_UPDATES)
        lines = incfile.readlines()
        incfile.close()
        return [l.strip() for l in lines]

    def getNbRequested(self, queries, update):
        count = 0
        for q in queries:
            if q.find(update.strip()) != -1:
                count += 1
        return count
