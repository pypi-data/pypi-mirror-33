/** Functions to boost certain calculations involving numpy.ndarray objects.
 *
 * These functions profit from the Python and Numpy C-API.
 *
 * @author: Miguel Ramos Pernas
 * @email:  miguel.ramos.pernas@cern.ch
 *
 */

// C-API
#include <Python.h>
#include "numpy/arrayobject.h"

// STD
#include <math.h>

// Local
#include "definitions.h"


/** Calculate the binary representation of a number.
 *
 */
npy_int _ibinary_repr( const npy_int i ) {

  npy_int c = i / 2;
  npy_int r = i % 2;

  if ( c != 0 )
    r += 10*_ibinary_repr(c);

  return r;
}


/** Calculate the binary representation (as an integer) of the values in an object.
 *
 * The object is converted to an array if necessary.
 */
static PyObject* ibinary_repr( PyObject *self, PyObject *args, PyObject *kwds ) {

  PyObject *in;

  static char* kwlist[] = {"arr", NULL};
  if ( !PyArg_ParseTupleAndKeywords(args, kwds, "O:ibinary_repr", kwlist, &in) )
    goto final;

  PyArrayObject* arr = (PyArrayObject*) PyArray_FROM_O(in);

  CHECK_INT_ARRAY(arr);

  // Initialize the output array
  PyArray_Descr* descr = PyArray_DescrFromType(NPY_INT);
  PyArrayObject* ret = (PyArrayObject*) PyArray_NewLikeArray(arr, NPY_ANYORDER, descr, 1);

  if ( PyArray_NDIM(arr) == 0 ) {

    const npy_int ae = *((npy_int*) arr->data);

    *((npy_int*) ret->data) = _ibinary_repr(ae);

    return (PyObject*) ret;
  }

  PyObject* ia = PyArray_IterNew((PyObject*) arr);
  PyObject* ir = PyArray_IterNew((PyObject*) ret);

  while ( PyArray_ITER_NOTDONE(ia) ) {

    npy_int* a_dt = (npy_int*) PyArray_ITER_DATA(ia);
    npy_int* r_dt = (npy_int*) PyArray_ITER_DATA(ir);

    // Calculate the greatest common divisor for this element
    *r_dt = _ibinary_repr(*a_dt);

    PyArray_ITER_NEXT(ia);
    PyArray_ITER_NEXT(ir);
  }

  Py_DECREF(ia);
  Py_DECREF(ir);

  return (PyObject*) ret;

 final:
  Py_XDECREF(arr);
  return NULL;
}


/** Function to calculate the bit length of a number.
 *
 * It is equivalent to the number of bits necessary to represent a number.
 */
npy_int _bit_length( const npy_int i ) {

  npy_int c = i / 2;
  npy_int r = i % 2;
  npy_int l = (c != 0 || r != 0);

  if ( c != 0 )
    l += _bit_length(c);

  return l;
}


/** Calculate the bit length of the values in an object.
 *
 * The object is converted to an array if necessary.
 */
static PyObject* bit_length( PyObject *self, PyObject *args, PyObject *kwds ) {

  PyObject *in;

  static char* kwlist[] = {"arr", NULL};
  if ( !PyArg_ParseTupleAndKeywords(args, kwds, "O:bit_length", kwlist, &in) )
    goto final;

  PyArrayObject* arr = (PyArrayObject*) PyArray_FROM_O(in);

  CHECK_INT_ARRAY(arr);

  // Initialize the output array
  PyArray_Descr* descr = PyArray_DescrFromType(NPY_INT);
  PyArrayObject* ret = (PyArrayObject*) PyArray_NewLikeArray(arr, NPY_ANYORDER, descr, 1);

  if ( PyArray_NDIM(arr) == 0 ) {

    const npy_int ae = *((npy_int*) PyArray_DATA(arr));

    *((npy_int*) PyArray_DATA(ret)) = _bit_length(ae);

    return (PyObject*) ret;
  }

  PyObject* ia = PyArray_IterNew((PyObject*) arr);
  PyObject* ir = PyArray_IterNew((PyObject*) ret);


  while ( PyArray_ITER_NOTDONE(ia) ) {

    npy_int* a_dt = (npy_int*) PyArray_ITER_DATA(ia);
    npy_int* r_dt = (npy_int*) PyArray_ITER_DATA(ir);

    // Calculate the greatest common divisor for this element
    *r_dt = _bit_length(*a_dt);

    PyArray_ITER_NEXT(ia);
    PyArray_ITER_NEXT(ir);
  }

  Py_DECREF(ia);
  Py_DECREF(ir);

  return (PyObject*) ret;

 final:
  Py_XDECREF(arr);
  return NULL;
}


/** Function to calculate the greatest common divisor of two numbers.
 *
 *  This function always returns a positive numbers, although
 *  "a" and "b" can be positive or negative.
 */
npy_int _gcd( npy_int a, npy_int b ) {

  while ( b ) {

    const npy_int r = a % b;

    a = b;
    b = r;
  }

  return abs(a);
}


/** Calculate the greatest common divisor function given two numpy.ndarray instances.
 *
 */
static PyObject* gcd( PyObject *self, PyObject *args, PyObject *kwds ) {

  PyObject* ina;
  PyObject* inb;

  static char* kwlist[] = {"a", "b", NULL};
  if ( !PyArg_ParseTupleAndKeywords(args, kwds, "OO:gcd", kwlist, &ina, &inb) )
    goto final;

  PyArrayObject* a = (PyArrayObject*) PyArray_FROM_O(ina);
  PyArrayObject* b = (PyArrayObject*) PyArray_FROM_O(inb);

  CHECK_INT_ARRAY(a);
  CHECK_INT_ARRAY(b);
  CHECK_DIM_ARRAYS(a, b);

  // Initialize the output array
  PyArray_Descr* descr = PyArray_DescrFromType(NPY_INT);
  PyArrayObject* ret = (PyArrayObject*) PyArray_NewLikeArray(a, NPY_ANYORDER, descr, 1);

  if ( PyArray_NDIM(a) == 0 && PyArray_NDIM(b) == 0 ) {

    const npy_int ae = *((npy_int*) a->data);
    const npy_int be = *((npy_int*) b->data);

    *((npy_int*) ret->data) = _gcd(ae, be);

    return (PyObject*) ret;
  }

  PyObject* ia = PyArray_IterNew((PyObject*) a);
  PyObject* ib = PyArray_IterNew((PyObject*) b);
  PyObject* ir = PyArray_IterNew((PyObject*) ret);

  while ( PyArray_ITER_NOTDONE(ia) ) {

    npy_int* a_dt = (npy_int*) PyArray_ITER_DATA(ia);
    npy_int* b_dt = (npy_int*) PyArray_ITER_DATA(ib);
    npy_int* r_dt = (npy_int*) PyArray_ITER_DATA(ir);

    // Calculate the greatest common divisor for this element
    *r_dt = _gcd(*a_dt, *b_dt);

    PyArray_ITER_NEXT(ia);
    PyArray_ITER_NEXT(ib);
    PyArray_ITER_NEXT(ir);
  }

  Py_DECREF(ia);
  Py_DECREF(ib);
  Py_DECREF(ir);

  return (PyObject*) ret;

 final:
  Py_XDECREF(a);
  Py_XDECREF(b);
  return NULL;
}


/** Definition of the functions to be exported.
 *
 */
PyMethodDef Methods[] = {

  {"bit_length", (PyCFunction) bit_length, METH_VARARGS|METH_KEYWORDS,
   "Determine the bit length of the elements of an array."},

  {"gcd", (PyCFunction) gcd, METH_VARARGS|METH_KEYWORDS,
   "Greatest common divisor calculated element by element in two arrays."},

  {"ibinary_repr", (PyCFunction) ibinary_repr, METH_VARARGS|METH_KEYWORDS,
   "Calculate the binary representation of the numbers in an array."},

  {NULL, NULL, 0, NULL}
};


/** Definition of the module.
 *
 */
#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef math_aux_cpy = {
  PyModuleDef_HEAD_INIT,
  "math_aux_cpy",
  "CPython functions for the 'math_aux' module.",
  -1,
  Methods
};
#endif


/** Function to initialize the module.
 *
 */
#if PY_MAJOR_VERSION >= 3

PyMODINIT_FUNC PyInit_math_aux_cpy( void ) {

#define INITERROR return NULL

#else

void initmath_aux_cpy( void ) {

#define INITERROR return

#endif

  import_array();

#if PY_MAJOR_VERSION >= 3
  PyObject* module = PyModule_Create(&math_aux_cpy);
#else
  PyObject* module = Py_InitModule("math_aux_cpy", Methods);
#endif

  if ( module == NULL )
    INITERROR;

#if PY_MAJOR_VERSION >= 3
  return module;
#endif
}
