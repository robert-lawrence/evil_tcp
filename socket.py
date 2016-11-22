


###Outline for socket.py


class Socket:


    def __init__(self, socket, host, port):
        """
        Not sure if host is necessary
        Socket will be the socket obj created by master.py with args host & port
        """
        pass


    def accept(self):
        """
        called by client code - Socket and connection threads should not touch!
        blocks until a new connection is received and a Connection object has 
        been created.
        
        Return: a Connection instance
        Errors: if socket closed, throw exception
        """
        pass


    def connect(self, host, port):
        """
        Called by client code - socket and connection threads should not touch!
        blocks while attempting to establish a connection with specified server

        Return: a Connection instance (if successful) or an error
        Errors: if socket closed, throw exception
        """
        pass


    def main(self):
        """
        Main loop 
        #TODO
        """
        pass

