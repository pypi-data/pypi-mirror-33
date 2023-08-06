##-*- coding: utf-8 -*-

class ConnectionInfo:
    """
    Contains all the informations to connect to the database.
    """

    def __init__(self,host=None,port=None,database=None,user=None,
                    password=None):
        self.setHost(host)
        self.setPort(port)
        self.setDatabase(database)
        self.setUser(user)
        self.setPassword(password)

    def setHost(self,host):
        assert ((isinstance(host,str)) or host == None)
        self.host = host
    
    def setPort(self,port):
        assert (isinstance(port,int) or port == None)
        self.port = port

    def setDatabase(self,database):
        assert (isinstance(database,str) or database == None)
        self.database = database

    def setUser(self, user):
        assert (isinstance(user,str) or user == None)
        self.user = user

    def setPassword(self, password):
        assert (isinstance(password, str) or password == None)
        self.password = password

    def getHost(self):
        return self.host
    
    def getPort(self):
        return self.port

    def getDatabase(self):
        return self.database

    def getUser(self):
        return self.user

    def getPassword(self):
        return self.password
