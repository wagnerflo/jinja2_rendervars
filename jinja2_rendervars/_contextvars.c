#define PY_SSIZE_T_CLEAN
#include <Python.h>

static inline int require_nargs(const char* name, Py_ssize_t nargs, Py_ssize_t expected) {
  if (nargs != expected) {
    PyErr_Format(
      PyExc_TypeError,
      "%s() expected %i arguments but got %i instead",
      name, expected, nargs
    );
  }
  return nargs != expected;
}

static PyObject* enter_context(PyObject* m, PyObject* const* args, Py_ssize_t nargs) {
  if (require_nargs("enter_context", nargs, 1)) {
    return NULL;
  }

  if (PyContext_Enter(args[0])) {
    return NULL;
  }

  Py_RETURN_NONE;
}

static PyObject* exit_context(PyObject* m, PyObject* const* args, Py_ssize_t nargs) {
  if (require_nargs("exit_context", nargs, 1)) {
    return NULL;
  }

  if (PyContext_Exit(args[0])) {
    return NULL;
  }

  Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
  { "enter_context", (PyCFunction) enter_context, METH_FASTCALL, NULL },
  { "exit_context",  (PyCFunction) exit_context,  METH_FASTCALL, NULL },
  { NULL, NULL, 0, NULL }
};

static struct PyModuleDef module = {
  PyModuleDef_HEAD_INIT,
  "jinja2_rendervars._contextvars",
  NULL,
  -1,
  methods
};

PyMODINIT_FUNC PyInit__contextvars(void) {
  return PyModule_Create(&module);
}
