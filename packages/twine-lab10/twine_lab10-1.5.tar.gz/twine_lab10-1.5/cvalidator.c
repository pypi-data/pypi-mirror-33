#include <Python.h>

static PyObject* cvalidator_is_in_bounds(PyObject *self, PyObject *args) {

    /* Declare the variable */
    float n;

    /* Parse the arguments */
    if(!PyArg_ParseTuple(args, "f", &n)){
        return NULL;
    }

    return ( n <= 0.0 || n > 10) ? Py_False : Py_True;
}

static PyMethodDef cvalidator_methods[] = {
    /* Register the function */
    {"is_in_bounds", cvalidator_is_in_bounds, METH_VARARGS,
     "Checks if number is in correct bounds"},
    /* Indicate the end of the list */
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef cvalidator_module = {
    PyModuleDef_HEAD_INIT,
    "cvalidator", /* Module name */
    NULL, /* Module documentation */
    -1, /* Module state, -1 means global. This parameter is
           for sub-interpreters */
    cvalidator_methods,
};

/* Initialize the module */
PyMODINIT_FUNC PyInit_cvalidator(void){
    return PyModule_Create(&cvalidator_module);
}
