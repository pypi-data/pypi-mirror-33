#ifndef BITPRIM_PY_P2P_H_
#define BITPRIM_PY_P2P_H_

#include <Python.h>

#ifdef __cplusplus
extern "C" {  
#endif  

PyObject* bitprim_native_p2p_address_count(PyObject* self, PyObject* args);
PyObject* bitprim_native_p2p_stop(PyObject* self, PyObject* args);
PyObject* bitprim_native_p2p_close(PyObject* self, PyObject* args);
PyObject* bitprim_native_p2p_stopped(PyObject* self, PyObject* args);

#ifdef __cplusplus
} //extern "C"
#endif  

#endif //BITPRIM_PY_P2P_H_
