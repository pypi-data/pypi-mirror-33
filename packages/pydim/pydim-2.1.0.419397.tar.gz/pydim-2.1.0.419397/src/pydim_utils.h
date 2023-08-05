/** **************************************************************************
 * \brief Utility functions to used for creating the PyDim module.
 * These are used primarily for converting between DIM C buffers and python
 * objects.
 *
 * \authors M. Frank, N. Neufeld, R. Stoica
 * \date Nov. 2007 - September 2008
 *
 * Various defines necessary for converting between the dim buffers and Python
 * objects.
 *
 * TODO: All the tests until were done communicating between the same
 * architectures (32 bits and 64 bits). Not sure DIM supports communicating
 * between platforms that have different sizes for the basic types.
 * Anyway I can't fix this if DIM doesn't support this.
 * *************************************************************************/

#ifndef PYDIM_UTILS_H
#define PYDIM_UTILS_H

// includes
extern "C" {
#include <Python.h>
#include <limits.h>
#include "structmember.h"
}
#include <dic.hxx>
#include <cstdlib>
#include <cstdio>
#include <map>
#include <string>


#ifdef _WIN32
 #include <cstdarg>
  static inline void ___print(const char* fmt,...)
  {
    va_list args; va_start(args,fmt);
    vprintf(fmt,args); printf("\n"); va_end(args);
  }
 #define print printf("DIM Wrapper: %s:%u ::%s: ", __FILE__, __LINE__, __FUNCTION__); ___print
#else
 #define print(...) printf("DIM Wrapper: %s:%u ::%s: ", __FILE__, __LINE__, __FUNCTION__); printf(__VA_ARGS__); printf("\n");
#endif

#ifdef __DEBUG
 #define debug print
 #define debugPyObject printPyObject
#else
 #define debug(...) /* __VA_ARGS__ */
 #define debugPyObject(...) /* __VA_ARGS__ */
#endif

#ifndef HOST_NAME_MAX
#define HOST_NAME_MAX _POSIX_HOST_NAME_MAX
#endif

#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE do { Py_INCREF(Py_None); return Py_None; } while(0);
#endif
#define errmsg(x) do { fprintf(stderr, "%s: %s\n", __FUNCTION__, x); } while(0);

#define _DIM_INT 0
#define _DIM_INT_LEN sizeof(int)

#define _DIM_FLOAT 1
#define _DIM_FLOAT_LEN sizeof(float)

#define _DIM_DOUBLE 2
#define _DIM_DOUBLE_LEN sizeof(double)

#define _DIM_XTRA 3
#define _DIM_XTRA_LEN sizeof(long long)

#define _DIM_STRING 4
#define _DIM_CHAR_LEN 1

#define _DIM_SHORT 5
#define _DIM_SHORT_LEN sizeof(short)

#define _DIM_LONG 6
#define _DIM_LONG_LEN sizeof(long)

#define MUL_INFINITE -1
/* multiplicity == MUL_INFINITE  means an arbitrary amount of data types
 *                  (e.g. ..;I)
 * multiplicity == 0 is an illegal value and will not be returned by this
 *                 function
 */


/* **************************************************************************
* Cache of commands format definitions
* *************************************************************************/
typedef std::map<std::string,std::string> CacheCmndFormat;

/**
*  This function activates the cache where format of commands are stored
*/
void activate_cmnd_format_cache();

/**
* This function reset the cache where format of commands are stored
*/
void reset_cmnd_format_cache();


 /**
 *  This function deactivate the cache where format of commands are stored
 */
 void deactivate_cmnd_format_cache();

 /**
 *  This function check if the cache where format of commands are stored is activated or not
 *  Output: 1 if cache is activated, 0 if not
 */
 int cache_activated();

 /**
 *  This function retieve the format of the command that name is passed in parameter
 *  from the cache where the format of commands are stored
 *  Input: command_name, the name of the command to get the format
 *  Output: the format of the command if the command is in the cache, NULL if not
 */
 char *get_format_of_cmnd_from_cache(char *command_name);

 /**
 *  This function insert the command name and its format in the cache
 *  where the format of the commands are stored
 *  Input:
 *    command_name: The name of the command to store the format
 *    format: The format of the command to store
 */
 void insert_format_of_cmnd_in_cache(char *command_name, char *format);

 /* **************************************************************************
 * End of cache of commands format definitions
 * *************************************************************************/

 /* **************************************************************************
  * Utility functions
  * *************************************************************************/
 #ifndef DIMCPP_MODULE
 int listOrTuple2Int(PyObject* pyObj, int** buffer);
 PyObject* stringList_to_tuple (char* services);
 PyObject* pyCallFunction (PyObject* pyFunc, PyObject* args);
 #endif

 #ifdef __DEBUG
 void printPyObject(PyObject *object);
 void printDimBuf(const char *buf, int size);
 PyObject* list2Tuple(PyObject* list);
 #endif

 #ifndef DIMC_MODULE
 int verify_dim_format(const char *format);
 int next_element(const char *schema, unsigned int *p, int *type, int *mult);
 PyObject * dim_buf_to_list(const char *schema, const char *buf, unsigned int len);
 #endif

 PyObject* dim_buf_to_tuple(const char *schema, const char *buf, int len);
 int getSizeFromFormat(const char* format);
 unsigned int getElemNrFromFormat(const char *format);

 unsigned int getSizeFromFormatAndObjects(PyObject *iter, const char* format);

 int iterator_to_buffer(PyObject *iter, char *buffer, unsigned int size, const char   *format);
 int iterator_to_allocated_buffer(PyObject  *iter, const char   *format, char  **buffer, unsigned int *size );

 char * get_format_of_service_from_dns(const char *service_name);

 char *get_format(char *service_name);

#endif
