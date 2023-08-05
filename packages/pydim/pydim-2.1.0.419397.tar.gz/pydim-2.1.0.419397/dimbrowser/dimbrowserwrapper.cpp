extern "C" {
  #include <Python.h>
  #include <dic.hxx>

  /**
  * Construct an instance of DimBrowser
  */
  DimBrowser *DimBrowser_new(){
    return new DimBrowser();
  }

  /**
  * Destroy the instance of DimBrowser passed in parameter
  */
  void DimBrowser_delete(DimBrowser *dbr){
    delete dbr;
  }

  /**
  * Call the DimBrowser's getServices() method
  * Input:
  *   dbr : The DimBrowser's instance
  *   wildcardServiceName : the service name with or without wildcard
  * Output:
  *   The number of services found by the DNS
  */
  int getServicesFromDNS(DimBrowser *dbr,char *wildcardServiceName){
    int nbServices = dbr->getServices(wildcardServiceName);
    return nbServices > 0 ? nbServices - 1 : 0; /* Bug in DimBrowser, the getServices method returns the number of services + 1*/
  }

  /**
  * Call the DimBroser's getNextService(char *serviceName, char *format) method
  * Has to be called after a getServicesFromDNS(char *wildCardServiceName) call
  * Input:
  *   dbr : The DimBrowser's instance
  * Output:
  *   A Python tuple containing the type of the service, its name and its format
  *   None if there is no service left to retrieve
  */
  PyObject *getNextServiceFromDNS(DimBrowser *dbr){
    long type;
    char *service_name, *service_format;
    PyObject *tuple_to_return, *py_type, *py_service_name, *py_format;

    type = (long)dbr->getNextService(service_name,service_format);

    if(type != 0){
      tuple_to_return = PyTuple_New(3);

      py_type = PyInt_FromLong(type);
      py_service_name = PyString_FromString(service_name);
      py_format = PyString_FromString(service_format);

      PyTuple_SetItem(tuple_to_return,0,py_type);
      PyTuple_SetItem(tuple_to_return,1,py_service_name);
      PyTuple_SetItem(tuple_to_return,2,py_format);

      return tuple_to_return;
    }
    /*No Service to retreive, return None*/
    Py_INCREF(Py_None);
    return Py_None;
  }

  /**
  * Call the DimBrowser's getServers() method
  * Input :
  *   dbr : The DimBrowser's instance
  * Output :
  *   The number of servers registered on the DNS
  */
  int getServersFromDNS(DimBrowser *dbr){
    return dbr->getServers();
  }

  /**
  * Call the DimBrowser's getNextServerFromDNS(char *serverName,char *node) method
  * Has to be called after a getServersFromDNS() call
  * Input:
  *   dbr : The DimBrowser's instance
  * Output:
  *   A Python tuple containing the name of the server returned
  *   by the DNS and the node where it is
  *   Returns None if there is no server left to retrieve
  */
  PyObject *getNextServerFromDNS(DimBrowser *dbr){
    char *server_name, *node;
    int isServersInList;
    PyObject *tuple_to_return, *py_server_name, *py_node;

    isServersInList = dbr->getNextServer(server_name,node);
    if(isServersInList){
      tuple_to_return = PyTuple_New(2);

      py_server_name = PyString_FromString(server_name);
      py_node = PyString_FromString(node);

      PyTuple_SetItem(tuple_to_return,0,py_server_name);
      PyTuple_SetItem(tuple_to_return,1,py_node);

      return tuple_to_return;
    }
    /*No Server to retrieve, return None*/
    Py_INCREF(Py_None);
    return Py_None;
  }

  /**
  * Call the DimBrowser's getServerServices(char *serverName)
  * Input:
  *   dbr : The DimBrowser's instance
  *   serverName : The name of the server to get all its services
  * Output:
  *   The number of services registered in the server where the name
  *   has been provided in parameters
  */
  int getServerServicesFromDNS(DimBrowser *dbr,char *serverName){
    int nbServices = dbr->getServerServices(serverName);
    return nbServices > 0 ? nbServices - 1 : 0; /* Bug in DimBrowser, the getServerServices method returns the number of services + 1*/
  }

  /**
  * Call the DimBrowser's getNextServerService(char *service_name, char *format)
  * Has to be called after the getServerServicesFromDNS(char *serverName)
  * Input:
  *   dbr: The DimBrowser's instance
  *   serverName: The name of the server ti get all its services
  * Output:
  *   A Python tuple containing the type of the service,  its name and its format
  *   None if there is no service left to retrieve
  */
  PyObject *getNextServerServiceFromDNS(DimBrowser *dbr){
    char *service_name, *service_format;
    long service_type;
    PyObject *tuple_to_return, *py_service_type ,*py_service_name, *py_service_format;

    service_type = dbr->getNextServerService(service_name,service_format);

    if(service_type != 0){
      tuple_to_return = PyTuple_New(3);

      py_service_type = PyInt_FromLong(service_type);
      py_service_name = PyString_FromString(service_name);
      py_service_format = PyString_FromString(service_format);

      PyTuple_SetItem(tuple_to_return,0,py_service_type);
      PyTuple_SetItem(tuple_to_return,1,py_service_name);
      PyTuple_SetItem(tuple_to_return,2,py_service_format);

      return tuple_to_return;
    }
    /*No service to retrieve, return None*/
    Py_INCREF(Py_None);
    return Py_None;
  }

  /**
  * Call the DiMBrowser's getServerClients(char *serverName) method
  * Input:
  *   dbr: The DimBrowser's instance
  *   serverName: The name of the server that we want to get all the clients connected
  * Output:
  *   dbr: The DimBrowser's instance
  *   serverName: the number of clients connected to the server corresponding to
  *   the named provided in parameters
  */
  int getServerClientsFromDNS(DimBrowser *dbr,char *serverName){
    return dbr->getServerClients(serverName);
  }

  /**
  * Call the DimBrowser's getNextServerClient(char *serverName, char *node) method
  * Has to be called after the getServerClientsFromDNS(DimBrowser *dbr, char *serverName)
  * Input:
  *   dbr: The DimBrowser's instance
  * Output:
  *   A Python Tuple that contains the client name
  *   None if there is no client left to retrieve
  */
  PyObject *getNextServerClientFromDNS(DimBrowser *dbr){
    char *client_name, *node;
    PyObject *tuple_to_return, *py_client_name, *py_node;
    int isClientInList;

    isClientInList = dbr->getNextServerClient(client_name,node);
    if(isClientInList != 0){
        tuple_to_return = PyTuple_New(2);

        py_client_name = PyString_FromString(client_name);
        py_node = PyString_FromString(node);

        PyTuple_SetItem(tuple_to_return,0,py_client_name);
        PyTuple_SetItem(tuple_to_return,1,py_node);

        return tuple_to_return;
    }
    Py_INCREF(Py_None);
    return Py_None;
  }
}
