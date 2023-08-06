class DBConnector:
    
    def connect(self):
        """
        Establish a connection with the database.
        returns: The connection object.
        """
        raise Exception("DbConnector-connect: DbConnector is abstract and "
                            "should not be called directly")

    def getConnection(self):
        """
        returns: The connection object if connected. None otherwise.
        """
        raise Exception("DbConnector-getConnection: DbConnector is abstract "
                            "and should not be called directly")
