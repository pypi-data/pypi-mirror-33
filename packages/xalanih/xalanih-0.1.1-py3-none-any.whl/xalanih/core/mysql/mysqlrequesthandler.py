from xalanih.core.requesthandler import RequestHandler
from xalanih.core.constants import Constants


class MysqlRequestHandler(RequestHandler):

    def requestXalanihTable(self):
        """
        Returns the request to check if the Xalanih table exists.
        """
        return "SHOW TABLES like '{0}'".format(Constants.XALANIH_TABLE)

    def requestXalanihTableCreation(self):
        """
        Returns the request that create the Xalanih table.
        """
        return ("CREATE TABLE {0} ("
                "`{1}` INT UNSIGNED NOT NULL AUTO_INCREMENT,"
                "`{2}` VARCHAR(150) NOT NULL,"
                "`{3}` TIME NOT NULL,"
                "PRIMARY KEY (`{1}`));").format(Constants.XALANIH_TABLE,
                                                Constants.COL_ID,
                                                Constants.COL_UPDT_NAME,
                                                Constants.COL_UPDT_TIME)

    def requestUpdateRecording(self):
        """
        Returns the request that insert an update.
        """
        return ("INSERT INTO {0} "
                "(`{1}`, `{2}`) "
                "VALUES (%s, NOW())").format(Constants.XALANIH_TABLE,
                                                Constants.COL_UPDT_NAME,
                                                Constants.COL_UPDT_TIME)
    
    def requestUpdate(self):
        """
        Returns the request that select an update.
        """
        return "SELECT * FROM {0} WHERE {1} = %s".format(
                                                Constants.XALANIH_TABLE,
                                                Constants.COL_UPDT_NAME)
