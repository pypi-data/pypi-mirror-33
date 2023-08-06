import logging

class Logger:
    
    def __init__(self, logfile, verbosity):
        level = self.__getLogLevel(verbosity)
        self.logger = logging.getLogger("xalanih")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.__getConsoleHandler(level))
        if logfile != None:
            self.logger.addHandler(self.__getFileHandler(logfile))

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def shutdown(self):
        logging.shutdown()

    def __getLogLevel(self, verbosity):
        if verbosity == 0:
            return 60
        elif verbosity == 1:
            return logging.ERROR
        elif verbosity == 2:
            return logging.WARNING
        elif verbosity == 3:
            return logging.INFO
        elif verbosity == 4:
            return logging.DEBUG
        return logging.INFO

    def __getFileHandler(self, logfile):
        handler = logging.FileHandler(logfile, mode="w")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.__getFileFormatter())
        return handler

    def __getConsoleHandler(self, level):
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(self.__getConsoleFormatter())
        return handler

    def __getFileFormatter(self):
        return logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")

    def __getConsoleFormatter(self):
        return logging.Formatter("%(levelname)s: %(message)s")
