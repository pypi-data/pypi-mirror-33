##-*- coding: utf-8 -*-
import argparse
from xalanih.core.connectioninfo import *
from xalanih.core.constants import Constants

class Parameters:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Xalanih: Database versioning helper.")
        # Action param
        self.parser.add_argument("action",
                choices=[Constants.ACTION_CREATE, Constants.ACTION_UPDATE],
                help="Give the action to execute. create: Create \
                the database from zero. update: execute the needed \
                update scripts on an existing database")

        # DB files directory
        self.parser.add_argument("-d","--directory", dest= "directory",
                default=".")

        # DB Type
        self.parser.add_argument("-t", "--type",
                choices=[Constants.DB_MYSQL], dest="type"
                ,default=Constants.DB_MYSQL,
                help="Select the type of database. (i.e. mysql)")

        # Host
        self.parser.add_argument("-H", "--host", dest="host",
                default="localhost", help="The hostname of the database")

        # Port
        self.parser.add_argument("-p", "--port", dest="port",
                default="3306",
                help="The port of the database")

        # DB
        self.parser.add_argument("database", help="The database")

        # User
        self.parser.add_argument("-u", "--user", dest="user", default="root")
        
        # Password
        self.parser.add_argument("-pwd", "-password", dest="password")

        # Socket
        self.parser.add_argument("-s", "--socket", dest="socket")

        # Logging
        self.parser.add_argument("-l", "--logfile", dest="logfile")

        self.parser.add_argument("-v", "--verbosity", dest="verbosity",
                choices=['0', '1', '2', '3', '4'], default='3',
                help="Define the verbosity of the application."
                        " 0=No log. 1=Errors. 2=Warnings."
                        " 3=Informations(Default). 4=Full verbosity.")

        # Last update
        self.parser.add_argument("-to","--to", dest="last_update",
                help="Set the name of the last update that must be executed.")

        self.parser.add_argument("-nu", "--noupdate", action="store_true",
                dest="no_update",
                help="If this flag is set, the script will not execute any " 
                        "update after the creation script. This flag has "
                        "only an effect when Xalanih is called for creation.")
                
        self.args = self.parser.parse_args()

        # Define connection info
        self.__defineConnectionInfo()

    def __defineConnectionInfo(self):
            assert self.args.port.isnumeric()
            self.connectionInfo = ConnectionInfo(host=self.args.host,
                        port=int(self.args.port), database=self.args.database,
                        user=self.args.user, password=self.args.password)

    def getArguments(self):
        return self.args

    def getAction(self):
        return self.args.action

    def getDirectory(self):
        return self.args.directory

    def getTypeOfDatabase(self):
        return self.args.type

    def getConnectionInfo(self):
            return self.connectionInfo

    def getSocket(self):
        return self.args.socket
        
    def getLogfile(self):
        return self.args.logfile

    def getVerbosity(self):
        return int(self.args.verbosity)

    def getLastUpdate(self):
        update = self.args.last_update
        if update != None and update.endswith(".sql"):
            return update[:-4]
        return update

    def getNoUpdate(self):
        return bool(self.args.no_update)
