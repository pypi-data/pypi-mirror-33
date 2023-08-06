class RequestHandler:

    def requestXalanihTable(self):
        """
        Returns the request to check if the Xalanih table exists.
        """
        raise Exception("RequestHandler is an abstract and " 
                "should not be called directly.")

    def requestXalanihTableCreation(self):
        """
        Returns the request that create the Xalanih table.
        """
        raise Exception("RequestHandler is an abstract and " 
                "should not be called directly.")

    def requestUpdateRecording(self):
        """
        Returns the request that insert an update.
        """
        raise Exception("RequestHandler is an abstract and " 
                "should not be called directly.")

    def requestUpdate(self):
        """
        Returns the request that select an update.
        """
        raise Exception("RequestHandler is an abstract and " 
                "should not be called directly.")
