#include <Python.h>
#include "add.h"

// Declare each module method
static PyObject *_add_add(PyObject *self, PyObject *args);

// Define an array of module methods
static PyMethodDef module_methods[] = {
	{"add", _add_add, METH_VARARGS, "Add doubles"}
};

// Define this module
static struct PyModuleDef _add = {
	PyModuleDef_HEAD_INIT,
	"_add",
	"DOCUMENTATION: A set of arithmetics",
	-1,
	module_methods
};

// Create module object
PyMODINIT_FUNC PyInit__add(void) {
	return PyModule_Create(&_add);
}

// Define module methods
static PyObject *_add_add(PyObject *self, PyObject *args) {
	double a, b;
	if (!PyArg_ParseTuple(args, "dd", &a, &b)) { return NULL; }

	double result_value = add(a, b);

	PyObject *result_tuple = Py_BuildValue("d", result_value);
	return result_tuple;
};


