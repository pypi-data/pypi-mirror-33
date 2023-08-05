/**
 * Copyright (c) 2017-2018 Bitprim developers (see AUTHORS)
 *
 * This file is part of Bitprim.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "p2p.h"
#include <bitprim/nodecint.h>
#include "../utils.h" //TODO(fernando): poner bien el dir del header


#ifdef __cplusplus
extern "C" {  
#endif  

// uint64_t /*size_t*/ p2p_address_count(p2p_t p2p);
// void p2p_stop(p2p_t p2p);
// void p2p_close(p2p_t p2p);
// int /*bool*/ p2p_stopped(p2p_t p2p);


PyObject* bitprim_native_p2p_address_count(PyObject* self, PyObject* args) {
    PyObject* py_p2p;

    if ( ! PyArg_ParseTuple(args, "O", &py_p2p)) {
        return NULL;
    }

    p2p_t p2p = (p2p_t)get_ptr(py_p2p);
    uint64_t res = p2p_address_count(p2p);
    return Py_BuildValue("K", res);
}

PyObject* bitprim_native_p2p_stop(PyObject* self, PyObject* args) {
    PyObject* py_p2p;

    if ( ! PyArg_ParseTuple(args, "O", &py_p2p)) {
        return NULL;
    }

    p2p_t p2p = (p2p_t)get_ptr(py_p2p);
    p2p_stop(p2p);
    Py_RETURN_NONE;
}

PyObject* bitprim_native_p2p_close(PyObject* self, PyObject* args) {
    PyObject* py_p2p;

    if ( ! PyArg_ParseTuple(args, "O", &py_p2p)) {
        return NULL;
    }

    p2p_t p2p = (p2p_t)get_ptr(py_p2p);
    p2p_close(p2p);
    Py_RETURN_NONE;
}

PyObject* bitprim_native_p2p_stopped(PyObject* self, PyObject* args) {
    PyObject* py_p2p;

    if ( ! PyArg_ParseTuple(args, "O", &py_p2p)) {
        return NULL;
    }

    p2p_t p2p = (p2p_t)get_ptr(py_p2p);
    int res = p2p_stopped(p2p);
    return Py_BuildValue("i", res);   
}

#ifdef __cplusplus
} //extern "C"
#endif  

