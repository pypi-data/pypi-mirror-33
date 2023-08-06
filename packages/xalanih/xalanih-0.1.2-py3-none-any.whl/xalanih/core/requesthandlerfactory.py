from xalanih.utils.parameters import Parameters
from xalanih.core.mysql.mysqlrequesthandler import MysqlRequestHandler
from xalanih.core.xalanihexception import XalanihException
from xalanih.core.constants import Constants


class RequestHandlerFactory:
    @staticmethod
    def getRequestHandler(params):
        """
        Get the RequestHandler object linked to the type of database.
        arguments:
        - params: The Parameters of the script.
        returns: The RequestHandler object linked to the type of database.
        throws: XalanihException if the kind of db is not supported.
        """
        assert isinstance(params,Parameters)
        dbType = params.getTypeOfDatabase()
        if(dbType == Constants.DB_MYSQL):
            return MysqlRequestHandler()
        raise XalanihException("This type of database is not managed :" 
                                    + dbType + ".",
                                    XalanihException.DB_TYPE_NOT_SUPPORTED)
