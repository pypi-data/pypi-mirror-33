import MySQLdb as db
from xalanih.utils.parameters import Parameters
from xalanih.core.dbconnector import DBConnector
from xalanih.core.logger import Logger
from xalanih.core.xalanihexception import XalanihException

class MysqlConnector(DBConnector):

    def __init__(self, params, logger):
        """
        Constructor.
        arguments:
        - params: The parameters of the script.
        - logger: The logger.
        """
        assert isinstance(params, Parameters)
        assert isinstance(logger, Logger)
        self.connectionInfo = params.getConnectionInfo()
        self.socket = params.getSocket()
        self.logger = logger
        self.connection = None

    def connect(self):
        """
        Establish a connection with the database.
        returns: The connection object.
        """
        if self.connection != None:
            raise XalanihException("You are already connected",
                                         XalanihException.ALREADY_CONNECTED)
        self.connection = db.connect(**self.__getConnectArgument())
        self.logger.info("Connected.")
        return self.connection

    def getConnection(self):
        """
        returns: The connection object if connected. None otherwise.
        """
        return self.connection
        

    def __getConnectArgument(self):
        """
        Return the list of arguments used to connect to the mysql database.
        returns: The list of arguments used to connect to the mysql database.
        """
        arguments = dict()
        host = self.connectionInfo.getHost()
        port = self.connectionInfo.getPort()
        database = self.connectionInfo.getDatabase()
        user = self.connectionInfo.getUser()
        password = self.connectionInfo.getPassword()

        arguments["host"] = host
        arguments["db"] = database
        arguments["user"] = user

        if port != None:
            arguments["port"] = port
        
        if password != None:
            arguments["passwd"] = password

        if self.socket!= None:
            arguments["unix_socket"] = self.socket

        return arguments
        
        



        


