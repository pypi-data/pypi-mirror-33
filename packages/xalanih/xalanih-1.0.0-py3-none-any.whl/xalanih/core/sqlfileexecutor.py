from xalanih.core.logger import Logger
import sqlparse


class SqlFileExecutor:
    @staticmethod
    def execute(connection, sqlFile, logger):
        """
        Execute the sql queries from a file.
        arguments:
        - sqlFile: The sql file to execute.
        - logger: The logger.
        """
        assert isinstance(logger, Logger)
        logger.debug("Executing SQL file: {0}".format(sqlFile.name))
        sql_statements = sqlparse.split(sqlFile.read())
        cursor = connection.cursor()
        for sql in sql_statements:
            if sql != "":
                logger.debug("[REQUEST] {0}".format(sql))
                cursor.execute(sql)
        cursor.close()
