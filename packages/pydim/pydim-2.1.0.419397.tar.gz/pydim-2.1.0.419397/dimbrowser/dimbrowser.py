import os
import sys
from ctypes import *
from ctypes.util import find_library
lib_folder_path = os.path.dirname(os.path.abspath(__file__))
dimbrowserwrapperlib = cdll.LoadLibrary(os.path.join(lib_folder_path,"..","dimbrowserwrappercpp.so"))

__docformat__ = 'reStructuredText'

class DimBrowser(object):
    """This class allows the user to interrogate the DIM DNS."""

    def __init__(self):
        """
        Create new instance of DimBrowser
        """
        self.obj = dimbrowserwrapperlib.DimBrowser_new()

    def __del__(self):
        """
        Destroy DimBrowser instance
        """
        dimbrowserwrapperlib.DimBrowser_delete(self.obj)


    def getServices(self,wildcardServiceName):
        """
        Check if a Service or Services (wildcards allowed) are available.

        :param str wildcardServiceName: The name of a service with or without wildcard (marked with \*)
        :return: The number of services / commands that match the search string.

        The :func:`getNextService()` method can be used to get the type of the services, their names and their format
        """
        return dimbrowserwrapperlib.getServicesFromDNS(self.obj,wildcardServiceName)

    def getNextService(self):
        """
        Has to be called **after** a :func:`getServices()` call.

        :return: This method is a **generator** that generates a tuple that has the following format : *(TypeOfService,NameOfService,FormatOfService)*

        If no service is found, the generator will generate None.
        """
        dimbrowserwrapperlib.getNextServiceFromDNS.restype = py_object
        res = 1
        while res != 0:
            tupleResult = dimbrowserwrapperlib.getNextServiceFromDNS(self.obj)
            if tupleResult == None:
                res = 0
            yield tupleResult

    def getServers(self):
        """
        Get the list of all servers available in the system.

        :return: The number of servers known by the DNS.

        The :func:`getNextServer()` method can be used to retrieve the server names and nodes.
        """
        return dimbrowserwrapperlib.getServersFromDNS(self.obj)


    def getNextServer(self):
        """
        Has to be called **after** a :func:`getServers()` call.

        :return: This method is a **generator** that generates a tuple that has the following format : *(NameOfServer,NodeNameWhereServerRuns)*

        If no server is found, the generator will generate None.
        """
        dimbrowserwrapperlib.getNextServerFromDNS.restype = py_object
        res = 1
        while res != 0:
            tupleResult = dimbrowserwrapperlib.getNextServerFromDNS(self.obj)
            if tupleResult == None:
                res = 0
            yield tupleResult

    def getServerServices(self,serverName):
        """
        Get the list of all services provided by a server.

        :param serverName: The name of the server to get his registered services.
        :return: The number of services provided by the server.

        The :func:`getNextServerService()` method can be used to retrieve the individual services and their formats.
        """
        return dimbrowserwrapperlib.getServerServicesFromDNS(self.obj,serverName)

    def getNextServerService(self):
        """
        Has to be called **after** a :func:`getServerServices` call.

        :returns: This method is a generator that **generates** a tuple that has the following format : *(TypeOfTheCommand,ServiceName,FormatOfService)*

        If no service is found, the generator will return None.
        """
        dimbrowserwrapperlib.getNextServerServiceFromDNS.restype = py_object
        res = 1
        while res != 0:
            tupleResult = dimbrowserwrapperlib.getNextServerServiceFromDNS(self.obj)
            if tupleResult == None:
                res = 0
            yield tupleResult

    def getServerClients(self,serverName):
        """
        Get the list of clients of a server.

        :param serverName: The name of the server to get its connected clients
        :return: The number of clients of the specified server.

        The :func:`getNextServerClient()` can be used to retrieve the individual client process names and nodes.

        **Warning:** The first time this function is called, the correct number of client is returned
        The second time, the number of clients will be increased by one : the first call makes you a client
        of the server !
        """
        return dimbrowserwrapperlib.getServerClientsFromDNS(self.obj,serverName)

    def getNextServerClient(self):
        """
        Has to be called **after** a :func:`getServerClients` call.

        :return: This method is a generator that generates a tuple that has the following format : *(ClientName,NodeNameWhereClientRuns)*

        If no client is found, the generator will return None.
        """
        dimbrowserwrapperlib.getNextServerClientFromDNS.restype = py_object
        res = 1
        while res != 0:
            tupleResult = dimbrowserwrapperlib.getNextServerClientFromDNS(self.obj)
            if tupleResult == None:
                res = 0
            yield tupleResult
