#include "pydim_utils.h"

 static int is_cache_activated = 1;

 static CacheCmndFormat cacheCmndFormat;

 /* **************************************************************************
 * Cache of commands format definitions
 * *************************************************************************/

 /**
 *  This function activates the cache where format of commands are stored
 */
 void activate_cmnd_format_cache(){
   is_cache_activated = 1;
 }

/**
* This function reset the cache where format of commands are stored
*/
 void reset_cmnd_format_cache(){
   cacheCmndFormat.erase(cacheCmndFormat.begin(),cacheCmndFormat.end());
 }

 /**
 *  This function deactivate the cache where format of commands are stored
 */
 void deactivate_cmnd_format_cache(){
   is_cache_activated = 0;
   reset_cmnd_format_cache();
 }

 /**
 *  This function check if the cache where format of commands are stored is activated or not
 *  Output: 1 if cache is activated, 0 if not
 */
 int cache_activated(){
   return is_cache_activated;
 }

 /**
 *  This function retieve the format of the command that name is passed in parameter
 *  from the cache where the format of commands are stored
 *  Input: command_name, the name of the command to get the format
 *  Output: the format of the command if the command is in the cache, NULL if not
 */
 char *get_format_of_cmnd_from_cache(char *command_name){
   std::string commandNameString(command_name);
   std::string format = cacheCmndFormat[commandNameString];
   if(format == ""){
     return NULL;
   }
   char *formatReturned = const_cast<char *>(format.c_str());/*new char[format.length()+1];
   strcpy(formatReturned,format.c_str());*/
   return formatReturned;
 }

 /**
 *  This function insert the command name and its format in the cache
 *  where the format of the commands are stored
 *  Input:
 *    command_name: The name of the command to store the format
 *    format: The format of the command to store
 */
 void insert_format_of_cmnd_in_cache(char *command_name, char *format){
   std::string commandNameString(command_name);
   std::string formatNameString(format);
   cacheCmndFormat[commandNameString] = formatNameString;
 }
/* **************************************************************************
* End of cache of commands format definitions
* *************************************************************************/

/* **************************************************************************
 * Utility functions
 * *************************************************************************/
#ifndef DIMCPP_MODULE
int listOrTuple2Int(PyObject* pyObj, int** buffer)
{
  int size, i, res=1;
  PyObject* tmp;

  if ( PyTuple_Check(pyObj) ) { //tuple
    size = PyTuple_Size(pyObj);
    if (!size)
      res = 0;
    (*buffer) = (int*)malloc(size*sizeof(int)+1);
    if ( !(*buffer) )
      res = 0;
    for (i=0; i<size; i++) {
      tmp = PyTuple_GetItem(pyObj, i);
      if (!tmp)
        res = 0;
      (*buffer)[i] = (int)PyInt_AsLong(tmp);
    }
  } else if ( PyList_Check(pyObj) ) { //list
    size = PyList_Size(pyObj);
    if (!size)
      res = 0;
    (*buffer) = (int*)malloc(size*sizeof(int)+1);
    if ( !(*buffer) )
      res = 0;
    for (i=0; i<size; i++) {
      tmp = PyList_GetItem(pyObj, i);
      if (!tmp)
        res = 0;
      (*buffer)[i] = (int)PyInt_AsLong(tmp);
    }
  } else
    res = 0;

  if (res) {
    (*buffer)[size] = 0;
    return 1;
  }
  else {
    free(*buffer);
    buffer = NULL;
    return 0;
  }
}
#endif

#ifndef DIMCPP_MODULE
PyObject* stringList_to_tuple (char* services)
{
  /* Gets a list of null terminated char* and converts it to a python tuple
  */
  PyObject* tuple=NULL;
  int i=0, size=0, start=0, cur=0;

  if (!services)
    return PyTuple_New(0); /* reference will be owned by the caller */
  /* getting the number of serviecs */
  while (services[i] != '\0') {
    if (services[i] == '\n')
      ++size;
  }
  tuple = PyTuple_New(size);
  i=0;
  while (services[i] != '\0') {
    if (services[i] == '\n') {
      PyTuple_SetItem(tuple, cur++,
          PyString_FromStringAndSize(&services[start], i-start));
      start=i+1;
    }
  }

  return tuple;
}
#endif

#ifndef DIMCPP_MODULE
PyObject* pyCallFunction (PyObject* pyFunc, PyObject* args)
{
  /*  Is the responsibility of the caller to handle the Ref count of both the
   * sentobject and the result.
   */
  PyGILState_STATE gstate;
  PyObject* res;

  gstate = PyGILState_Ensure();
  res = PyEval_CallObject(pyFunc, args);
  if (!res)
    PyErr_Print();
  PyGILState_Release(gstate);

  return res;
}
#endif

#ifdef __DEBUG
void printPyObject(PyObject *object)
{
  if (!object) return;
  PyObject_Print(object, stdout, Py_PRINT_RAW);
  printf("\n");
}

void printDimBuf(const char *buf, int size) {
  for (int i=0; i<size; i++)
    printf("Byte %d: ASCII %c, CODE: %d\n", i, buf[i], buf[i]);
}
#endif


#ifndef DIMC_MODULE
int verify_dim_format(const char *format)
{
  /* Return True in case of success and False otherwise
  */
  int ptr=0, x, newptr;
  int size=strlen(format);
  char delimiter=';';
  const char itemtypes[]="ICLSFDXiclsfdx";
  const char digits[]="0123456789";

  while (ptr<size) {
    for (newptr=ptr; newptr<size && format[newptr]!=delimiter; newptr++);
    /* We have found a new group of parameters */
    if (!strchr(itemtypes, format[ptr]))
      /* This means the type letter is unknown */
      return 0;
    if (ptr+1 == newptr) {
      /* Here we only have the item type letter. Checking to see if we are
       * at the end
       */
      if (newptr == size)
        /* We are at the end, newptr is on the \0 string terminating char */
        return 1;
      else
        /* in the middle of the format string the number of items is missing */
        return 0;
    } else {
      /* The multiplicity of the parameters is also specified */
      if (format[ptr+1] != ':')
        /* We were expecting a colon separator between the type
         * and the multiplicity
         */
        return 0;
      if (ptr+2 == newptr)
        /* This means that there is no digit after colon */
        return 0;
      for (x=ptr+2; x<=newptr-1; x++) {
        if (!strchr(digits, format[x]))
          /* We were expecting a digit */
          return 0;
      }
    } // end if-else
    ptr=newptr+1;
  } // end while

  return 1;
} // end verify_dim_format
#endif


  int
next_element(const char *schema, unsigned int *p, int *type, int *mult)
{
  /** \brief Incrementally parses a DIM format and returns the next element
   * from it
   * @param schema The string containing the DIM format
   * @param p At entry this contains the location inside the format buffer
   * from where the parsing should start. At return is updated to the end
   * element location.
   * @param type The type of the next element is returned using this parameter
   * @param mult The multiplicity of the next element. -1 means infinite
   * @return The status code of the function call succedded or not
   * (1 for success)
   */
  char *endptr;

  /* check to see if we haven't gone pass the schema string limit */
  if (*p >= strlen(schema))
    return 0;

  if (schema[*p] == '\0') return 0;
  switch (toupper(schema[*p])) {
    case 'I':
    case 'L': *type = _DIM_INT; break;
    case 'C': *type = _DIM_STRING; break;
    case 'F': *type = _DIM_FLOAT; break;
    case 'D': *type = _DIM_DOUBLE; break;
    case 'X': *type = _DIM_XTRA; break;
    case 'S': *type = _DIM_SHORT; break;
    default:
              print("Bad type character %c", schema[*p]);
              *type = -1;
              return 0;
  }
  switch (schema[++(*p)]) {
    case '\0': *mult = MUL_INFINITE; break;
               /* this is not stricly correct from DIM point of view. */
    case ';': *mult = 1; ++(*p); break;
    case ':':
              (*p)++;
              *mult = strtoul(&schema[*p], &endptr, 10);
              if (endptr == &schema[*p]) {
                print("illegal number\n");
                return 0;
              }
              *p += (endptr - &schema[*p]) + ((*endptr == ';') ? 1 : 0);
              break;
    default:
              print("Bad multiplicity character %c\n", schema[*p]);
              return 0;
  }

  return 1;
}


PyObject *
dim_buf_to_list(const char *schema, const char *buf, unsigned int len)
{
  /* NOTE: Compilers will pad structures to the arhitecture word size.
   * It is NOT recommended to pass the lenght of the buffer using
   * strlen() if the last type field of the format has multiplicity
   * unlimited. You will see garbage in the buffer after conversion!
   * Workarounds: disable padding from the declared structure and/or
   * specify the exact size of the buffer.
   */
  int j=0, type=0, mult=0, n=0;
  unsigned int m=0;
  PyObject *list, *tmp;
  float f;
  if (!(list = PyList_New(0))) {
    /* could not create a new Python list */
    print("ERROR: Could not create a Python list.");
    return NULL;
  }
  while (next_element(schema, &m, &type, &mult)) {
    switch (type) {
      case _DIM_INT:
        if (mult == MUL_INFINITE)
          mult = (len - n) / _DIM_INT_LEN;
        for (j = 0; j < mult; ++j)
          if (n + _DIM_INT_LEN <= len) {
            tmp = PyInt_FromLong(*(int *)&buf[n]);
            n += _DIM_INT_LEN;
            PyList_Append(list, tmp);
            Py_DECREF(tmp);
          } else goto short_buffer;
        break;
      case _DIM_FLOAT:
        if (mult == MUL_INFINITE)
          mult = (len - n) / _DIM_FLOAT_LEN;
        for (j = 0; j < mult; ++j)
          if (n + _DIM_FLOAT_LEN <= len) {
            f = *(float *)(&buf[n]);
            tmp = PyFloat_FromDouble(f);
            n += _DIM_FLOAT_LEN;
            PyList_Append(list, tmp);
            Py_DECREF(tmp);
          } else goto short_buffer;
        break;
      case _DIM_DOUBLE:
        if (mult == MUL_INFINITE)
          mult = (len - n) / _DIM_DOUBLE_LEN;
        for (j = 0; j < mult; ++j)
          if (n + _DIM_DOUBLE_LEN <= len) {
            tmp = PyFloat_FromDouble(*(double *)&buf[n]);
            n += _DIM_DOUBLE_LEN;
            PyList_Append(list, tmp);
            Py_DECREF(tmp);
          } else goto short_buffer;
        break;
      case _DIM_XTRA:
        if (mult == MUL_INFINITE)
          mult = (len - n) / _DIM_XTRA_LEN;
        for (j = 0; j < mult; ++j)
          if (n + _DIM_XTRA_LEN <= len) {
            tmp = PyLong_FromLongLong(*(long long *)&buf[n]);
            n += _DIM_XTRA_LEN;
            PyList_Append(list, tmp);
            Py_DECREF(tmp);
          } else goto short_buffer;
        break;
      case _DIM_STRING:
        if (mult == MUL_INFINITE)
          mult = (len - n) / _DIM_CHAR_LEN;
        if ((unsigned int)(n + mult) <= len) { // ugly
          int p = (mult-1) >= 0 ? (mult -1) : 0;
          //while (p && buf[n+p] == '\0')
          //  --p;
          tmp = PyString_FromStringAndSize(&buf[n], p+1);
          n += mult;
        } else {
          int p = ((int)len-n-1) >= 0 ? ((int)len-n-1) : 0;
          /* uncomment this is you want to strip '\0' from the string */
          // while (p && buf[p] == '\0')
          //  --p;
          tmp = PyString_FromStringAndSize(&buf[n], p+1);
          n = len;
        }
        PyList_Append(list, tmp);
        Py_DECREF(tmp);
        break;
      case _DIM_SHORT:
        if (mult == MUL_INFINITE)
          mult = (len - n) / _DIM_SHORT_LEN;
        for (j = 0; j < mult; ++j)
          if (n + _DIM_SHORT_LEN <= len) {
            // ugly
            tmp = PyInt_FromLong(*(short int *)&buf[n]);
            n += _DIM_SHORT_LEN;
            PyList_Append(list, tmp);
            Py_DECREF(tmp);
          } else goto short_buffer;
        break;
      default:
        goto short_buffer;
    } // end switch
  } // end while

  return list;

short_buffer:
  print("Provided buffer was to short to convert all the arguments using the DIM format specified." );
  print("Buffer size %d, format %s", len, schema);
  Py_XDECREF(list);
  return NULL;
}

#ifdef __DEBUG
PyObject*
list2Tuple(PyObject* list)
{
  int size, i;
  PyObject* tuple;

  if ( !PyList_Check(list) ) return NULL;
  size = PyList_Size(list);
  tuple = PyTuple_New(size);
  for(i=0; i<size; i++) {
    PyTuple_SetItem(tuple, i, PyList_GetItem(list, i) );
    //PyObject_Print( PyList_GetItem(list, i), stdout, Py_PRINT_RAW );
  }
  //  printPyObject(list);
  //  printPyObject(tuple);

  return tuple;
}
#endif

PyObject*
dim_buf_to_tuple(const char *schema, const char *buf, int len)
{
  PyObject *list, *tuple;

  list = dim_buf_to_list(schema, buf, len);
  if (!list) {
    print("ERROR: Could not convert DIM buffer to "
          "Python objects using the specified format");
    return NULL;
  }
  tuple = PyList_AsTuple(list);
  Py_DECREF(list);

  return tuple;
}


int
getSizeFromFormat(const char* format)
{
  int type=0, mult=0, size=0;
  unsigned int ptr=0;

  while ( next_element(format, &ptr, &type, &mult) ) {
    if (mult == -1) {
      // we can't calculate the maximum size in this case
      // 0 means error
      return 0;
    }
    switch (type) {
      case _DIM_LONG    : size += mult * _DIM_LONG_LEN;    break;
      case _DIM_INT     : size += mult * _DIM_INT_LEN;     break;
      case _DIM_STRING  : size += mult * _DIM_CHAR_LEN;    break;
      case _DIM_FLOAT   : size += mult * _DIM_FLOAT_LEN;   break;
      case _DIM_DOUBLE  : size += mult * _DIM_DOUBLE_LEN;  break;
      case _DIM_XTRA    : size += mult * _DIM_XTRA_LEN;    break;
      case _DIM_SHORT   : size += mult * _DIM_SHORT_LEN;   break;
      default:
        print("Bad type char extracted from (%c. Type is %d\n",
              format[ptr], type);
        return -1;
    }
  }

  return size;
}


  unsigned int
getElemNrFromFormat(const char *format)
{
  /* Receives a closed format string and returns the total number of
   * elements expected from it.
   * In case of any errors returns 0.
   */
  int type=0, mult=0, total=0;
  unsigned int ptr=0;

  while (next_element(format, &ptr, &type, &mult) ) {
    if (mult == -1) {
      // we can't calculate the maximum size in this case
      // 0 means error
      return 0;
    }
    switch (type) {
      case _DIM_LONG  :
      case _DIM_INT   :
      case _DIM_FLOAT :
      case _DIM_DOUBLE:
      case _DIM_XTRA  :
      case _DIM_SHORT : total += mult; break;
                        //in Python S:<number> is only one string
      case _DIM_STRING: ++total; break;
      default:
                        print("Bad type char extracted from (%c. Type is %d\n",
                            format[ptr], type);
                        return 0;
    }
  }

  return total;
}


//#ifndef DIMC_MODULE
  unsigned int
getSizeFromFormatAndObjects(PyObject *iter, const char* format)
{
  /* Returns the size needed for converting the Python iterator to a
   * buffer according to a DIM format. The format can have an unlimited
   * number of ending variables of the same type.
   */

  unsigned int format_size=0, iter_size=0, obj_nr=0, lastobj_size=0, total_size=0;
  const char itemtypes[]="ICLSFDXiclsfdx";
  char *temp_format;
  PyObject *last;

  format_size = strlen(format);
  if (!strchr(itemtypes, format[format_size-1])) {
    // this means we can deduct the size directly from format
    return getSizeFromFormat(format);
  }
  // we have an open ended format string
  if (!PySequence_Check(iter)) {
    print("Python object is not a sequence");
    return 0;
  }
  // Get the size of all fixed number of arguments (if they exist)
  if (format_size>1) {
    temp_format = new char[format_size];
    strncpy(temp_format, format, format_size-1);
    temp_format[format_size-1]='\0';
    total_size = getSizeFromFormat(temp_format);
    // Get the total number of objects for which the size was calculated
    obj_nr = getElemNrFromFormat(temp_format);
    delete temp_format;
  }

  // Get the total size of the sequence
  iter_size=PySequence_Size(iter);

  if (iter_size <= obj_nr) {
    /* Means the iterator does not contain enough elements
     * This should never be the case but i'm returning the total size
     * for the fixed parameters
     */
    return total_size;
  }
  // Get the size of the objects that follows
  switch (toupper(format[format_size-1])) {
    case 'L' :
    case 'I' : lastobj_size = _DIM_INT_LEN   ; break;
    case 'F' : lastobj_size = _DIM_FLOAT_LEN ; break;
    case 'D' : lastobj_size = _DIM_DOUBLE_LEN; break;
    case 'X' : lastobj_size = _DIM_XTRA_LEN  ; break;
    case 'S' : lastobj_size = _DIM_SHORT_LEN ; break;
    case 'C' :
               /* this is tricky: we only have a string of unlimited size
                * I have to get the string length and add it.
                * TODO: subsequent objects are ignored.
                */
               last = PySequence_GetItem(iter, obj_nr);
               if (!PyString_Check(last)) {
                 print("Invalid Python object expected a string");
                 return 0;
               }
               total_size += PyString_Size(last);
               Py_DECREF(last);
               return total_size;
               break;
    default:
               print("Bad type char (%c) extracted from %s",
                   format[format_size-1], format);
               return 0;
  }
  total_size = total_size + lastobj_size * (iter_size - obj_nr);

  return total_size;
}
//#endif


int
iterator_to_buffer(PyObject     *iter,   /* list or tuple PyObject */
                   char         *buffer, /* buffer to perform conversion */
                   unsigned int size,    /* maximum size of buffer */
                   const char   *format) /* the format to use */
{
  /** \brief This function gets a Python iterator and converts it to a
   * char* buffer according to the format specified.
   */
  int type=0, mult=0, j;
  PyObject *tmp, *tmp1;
  unsigned int ptr=0, buf_ptr=0, str_size=0, iter_size=0, elem=0;
  int i;
  float f;
  double d;
  short s;
  long l;
  long long x;
  char *str;

  memset(buffer, '\0', size);

  if (!PySequence_Check(iter)) {
    print("Provided Python object is not a sequence");
    return 0;
  }

  while (next_element(format, &ptr, &type, &mult) ) {
    for (j=0; j<mult || (mult==-1 && buf_ptr<size); j++) {
      tmp = PySequence_GetItem(iter, elem++);
      if(!tmp) {
        print("Iterator object does not hold enough values to match format");
        return 0;
      }
      switch (type) {
        case _DIM_INT :
          if(size < buf_ptr + _DIM_INT_LEN)
            goto shortbuffer;
          tmp1 = PyNumber_Int(tmp);
          if (!tmp1) goto invalid_format;
          i = PyInt_AsLong(tmp1);
          memcpy(&buffer[buf_ptr], &i, _DIM_INT_LEN);
          buf_ptr += _DIM_INT_LEN;
          break;
        case _DIM_LONG :
          if (size < buf_ptr + _DIM_LONG_LEN)
            goto shortbuffer;
          tmp1 = PyNumber_Long(tmp);
          if (!tmp1) goto invalid_format;
          l = PyInt_AsLong(tmp1);
          memcpy(&buffer[buf_ptr], &l, _DIM_LONG_LEN);
          buf_ptr += _DIM_LONG_LEN;
          break;
        case _DIM_STRING:
          /* Here I explicitly want to use PyObject_Str to convert the object to a
           * string. 'tmp' might be a random Python object that is converted
           * to a string.
           */
          tmp1 = PyObject_Str(tmp);
          str = PyString_AsString(tmp1);
          str_size = strlen(str)+1;
          if (mult==-1) {
            if ((buf_ptr+str_size)>size) {
              /* this means the Python string is too
               * big to be completely converted
               */
              memcpy(&buffer[buf_ptr], str, size-buf_ptr);
            } else {
              /* shorter string OR we have an end of line in the middle
               * I prefer here to copy past what size indicates. This allows
               * to pass also Null characters..*/
              //memcpy(&buffer[buf_ptr], str, str_size);
              //memset(&buffer[buf_ptr+str_size], '\0', size-buf_ptr-str_size);
              memcpy(&buffer[buf_ptr], str, size-buf_ptr);
            }
            buf_ptr = size;
          } else {
            if (str_size < (unsigned int)mult) {
              /* we have a shorter string */
              memcpy(&buffer[buf_ptr], str, str_size);
              /* zeroing what can't be filled */
              memset(&buffer[buf_ptr+str_size], '\0', mult-str_size);
            } else
              /* String is to big to fit in its place. Truncating */
              memcpy(&buffer[buf_ptr], str, mult);
            buf_ptr += _DIM_CHAR_LEN * mult;
            j = mult;
          }
          break;
        case _DIM_FLOAT:
          if (size < buf_ptr + _DIM_FLOAT_LEN)
            goto shortbuffer;
          tmp1 = PyNumber_Float(tmp);
          if (!tmp1) goto invalid_format;
          f = (float)PyFloat_AsDouble(tmp1);
          memcpy(&buffer[buf_ptr], &f, _DIM_FLOAT_LEN);
          buf_ptr += _DIM_FLOAT_LEN;
          break;
        case _DIM_DOUBLE:
          if (size < buf_ptr + _DIM_DOUBLE_LEN)
            goto shortbuffer;
          tmp1 = PyNumber_Float(tmp);
          if (!tmp1) goto invalid_format;
          d = PyFloat_AsDouble(tmp1);
          memcpy(&buffer[buf_ptr], &d, _DIM_DOUBLE_LEN);
          buf_ptr += _DIM_DOUBLE_LEN;
          break;
        case _DIM_XTRA:
          if (size < buf_ptr + _DIM_XTRA_LEN)
            goto shortbuffer;
          tmp1 = PyNumber_Long(tmp);
          if (!tmp1) goto invalid_format;
          x = PyLong_AsLongLong(tmp1);
          memcpy(&buffer[buf_ptr], &x, _DIM_XTRA_LEN);
          buf_ptr += _DIM_XTRA_LEN;
          break;
        case _DIM_SHORT:
          if (size < buf_ptr + _DIM_SHORT_LEN)
            goto shortbuffer;
          tmp1 = PyNumber_Int(tmp);
          if (!tmp1) goto invalid_format;
          //printPyObject(tmp1);
          s = (short int)PyInt_AsLong(tmp1);
          memcpy(&buffer[buf_ptr], &s, _DIM_SHORT_LEN);
          buf_ptr += _DIM_SHORT_LEN;
          break;
        default:
          print("bad character %c. Type is %d\n", format[ptr], type);
          return 0;
      }
      Py_DECREF(tmp);
      Py_DECREF(tmp1);
    }
  }
  iter_size = PySequence_Size(iter);
  if (iter_size != elem) {
    // Check to see if all the objects from the iterator were used
    print("WARNING: Python iterator holds more objects than DIM format specifies.");
    debug(" Dumping objects and format: ");
    debugPyObject(iter);
    debug("DIM Format: %s", format);
  }

  return 1;

shortbuffer:
  print("WARNING: The provided buffer is not big enough to hold all objects."
        " Truncating...");
  return 1;

invalid_format:
  print("WARNING: Python iterator holds more objects than DIM format specifies.");
    debug(" Dumping objects and format: ");
    debugPyObject(iter);
    debug("DIM Format: %s", format);

  Py_XDECREF(tmp);
  Py_XDECREF(tmp1);
  return 0;
}


//#ifdef DIMC_MODULE
int
iterator_to_allocated_buffer(PyObject  *iter, /* list or tuple */
                             const char   *format,  /* the format to use */
                             char  **buffer, /* conversion buffer */
                             unsigned int *size )/* maximum size of buffer */
{
  /** This function allocates a new buffer and converts the python
   * iterator objects according to 'format'.
   * Input: PyTuple or PyList
   * Output: pointer to the newly created buffer and its size
   */
  *buffer = NULL;
  *size = 0;

  *size = getSizeFromFormatAndObjects(iter, format);
  if (!*size) {
    // could not figure out the size of the needed buffer
    *buffer = NULL;
    return 0;
  }
  *buffer= (char*)malloc(*size);
  if (!iterator_to_buffer(iter, *buffer, *size, format)) {
    *buffer = NULL;
    return 0;
  }
    // the call succeded
    return 1;
}

/**
* This function returns from the DNS the format of the data waited by the service
* which the name is provided in parameters
* If the service's name provided doesn't correspond to an existing service
* the format returned is NULL.
* Input : service_name, the name of the service
* Output : the string format of the service if the service is found by the DNS, NULL otherwise
*/
char * get_format_of_service_from_dns(const char *service_name)
{
  DimBrowser dbr;
  char *current_service;
  char *format = NULL;
  int nb_services_returned_by_dns;
  nb_services_returned_by_dns = dbr.getServices(service_name);
  if(nb_services_returned_by_dns != 0)
    /* service found, retrieve the format from the DNS */
    dbr.getNextService(current_service,format);
  return format;
}

/**
* This function returns the format corresponding to the service name
* passed in parameters.
* It retrieves the format from the cache (if it not has been deactivated)
* or from the the DNS. It also insert the format found from the DNS in
* the cache (if it not has been deactivated)
* Input:
*   service_name: the name of the service to get the format
* Output:
*   The format of the service if the service exists or is found
*   NULL if not
*/
char *get_format(char *service_name){
  char *format = NULL;
  if(cache_activated()){
    format = get_format_of_cmnd_from_cache(service_name);
  }
  if(format == NULL){
    /* Format is not in the cache or cache is deactivated, try to get it from the DNS */
    format = get_format_of_service_from_dns(service_name);
    if(format != NULL){
      /*Format has been found, store it in the cache*/
      if(cache_activated()){
        /*Insert format of the command in the cache*/
        insert_format_of_cmnd_in_cache(service_name,format);
      }
    }
  }
  return format;
}

//#endif
