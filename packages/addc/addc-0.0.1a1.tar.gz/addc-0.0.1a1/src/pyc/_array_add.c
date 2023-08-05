#include <Python.h>
#include <numpy/arrayobject.h>
#include "array_add.h"

static PyObject *_array_add_add_array_double(PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
	{"add_array_double", _array_add_add_array_double, METH_VARARGS, "Add double-type array"}
};

static PyModuleDef _array_add = {
	PyModuleDef_HEAD_INIT,
	"_array_add",
	"A set of array arithmetics functions",
	-1,
	module_methods
}; 

PyMODINIT_FUNC PyInit__array_add(void) {
	import_array();
	return PyModule_Create(&_array_add);
}



static PyObject *_array_add_add_array_double(PyObject *self, PyObject *args) {
	PyObject *a_obj, *b_obj, *out_obj;
	long N;

	if (!PyArg_ParseTuple(args, "OOOl", &a_obj, &b_obj, &out_obj, &N)) { 
		PyErr_SetString(PyExc_Exception, "Failed to parse argument tuple");
		return NULL; }

	PyObject *a_array = PyArray_FROM_OTF(a_obj, NPY_DOUBLE, NPY_IN_ARRAY);
	PyObject *b_array = PyArray_FROM_OTF(b_obj, NPY_DOUBLE, NPY_IN_ARRAY);
	PyObject *out_array = PyArray_FROM_OTF(out_obj, NPY_DOUBLE, NPY_OUT_ARRAY);

	if (a_array == NULL || b_array == NULL || out_array == NULL) {
		PyErr_SetString(PyExc_Exception, "Failed to get array object from input arguments");
		Py_XDECREF(a_array);
		Py_XDECREF(b_array);
		Py_XDECREF(out_array);
		return NULL;
	}

	N = (long) PyArray_DIM(a_array, 0);

	double *a = (double *) PyArray_DATA(a_array);
	double *b = (double *) PyArray_DATA(b_array);
	double *out = (double *) PyArray_DATA(out_array);
	
	if (add_array_double(a, b, out, N) != 0) {
		PyErr_SetString(PyExc_Exception, "Failed to add_array_double()");
		Py_DECREF(a_array);
		Py_DECREF(b_array);
		Py_DECREF(out_array);
		return NULL;
	}

	//PyObject *ret = Py_BuildValue("O", out_obj);
	Py_INCREF(Py_None);

	Py_DECREF(a_array);
	Py_DECREF(b_array);
	Py_DECREF(out_array);

	//return ret;
	return Py_None;

}

