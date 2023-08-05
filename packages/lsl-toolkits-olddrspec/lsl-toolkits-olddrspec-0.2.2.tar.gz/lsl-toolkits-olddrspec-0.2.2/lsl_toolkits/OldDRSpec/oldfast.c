#include "Python.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <complex.h>

#include "numpy/arrayobject.h"

#define PI 3.1415926535898
#define imaginary _Complex_I

/*
Exceptions for the Go Fast! Readers
*/

static PyObject *syncError;
static PyObject *eofError;


/*
DR Spectrometer header format
*/

#pragma pack(push)
#pragma pack(1)
typedef struct {
    unsigned int MAGIC1; 			// must always equal 0xC0DEC0DE
    unsigned long long timeTag0;    // time tag of first frame in ``block''
    unsigned short int timeOffset;  // time offset reported by DP
    unsigned short int decFactor;   // decimation factor
    unsigned int freqCode[2];       // DP frequency codes for each tuning
                                    //   indexing: 0..1 = Tuning 1..2
    unsigned int fills[4];          // fills for each pol/tuning combination
                                    //   indexing: 0..3 = X0, Y0 X1, Y1
    unsigned char errors[4];        // error flag for each pol/tuning combo
                                    //   indexing: 0..3 = X0, Y0 X1, Y1
    unsigned char beam;             // beam number
    unsigned int nFreqs;            // <Transform Length>
    unsigned int nInts;             // <Integration Count>
    unsigned int satCount[4];       // saturation count for each pol/tuning combo
                                    //   indexing: 0..3 = X0, Y0 X1, Y1
    unsigned int MAGIC2;            // must always equal 0xED0CED0C
} DRSpecHeader;
#pragma pack(pop)


/*
DR Spectrometer Reader
*/

static PyObject *readDRSpec(PyObject *self, PyObject *args) {
    PyObject *ph, *buffer, *output, *frame, *fHeader, *fData, *temp;
    PyObject *tuningWords, *fills, *errors, *saturations;
    PyArrayObject *dataX0=NULL, *dataY0=NULL, *dataX1=NULL, *dataY1=NULL;
    int i, nSets=4;
    DRSpecHeader header;
    
    if(!PyArg_ParseTuple(args, "OO", &ph, &frame)) {
        PyErr_Format(PyExc_RuntimeError, "Invalid parameters");
        return NULL;
    }
    
    // Read in a single header
    buffer = PyObject_CallMethodObjArgs(ph, PyString_FromString("read"), PyInt_FromLong(sizeof(DRSpecHeader)), NULL);
    if( buffer == NULL ) {
        if( PyObject_HasAttrString(ph, "read") ) {
            PyErr_Format(PyExc_IOError, "An error occured while reading from the file");
        } else {
            PyErr_Format(PyExc_AttributeError, "Object does not have a read() method");
        }
        goto fail;
    } else if( PyString_GET_SIZE(buffer) != sizeof(DRSpecHeader) ) {
        PyErr_Format(eofError, "End of file encountered during filehandle read");
        goto fail;
    }
    memcpy(&header, PyString_AS_STRING(buffer), sizeof(header));
    Py_XDECREF(buffer);
    
    // Check the header's magic numbers
    if( header.MAGIC1 != 0xC0DEC0DE || header.MAGIC2 != 0xED0CED0C) {
        PyFile_DecUseCount((PyFileObject *) ph);
        PyErr_Format(syncError, "Sync word differs from expected");
        return NULL;
    }
    
    // Create the output data arrays
    npy_intp dims[1];
    dims[0] = header.nFreqs;
    dataX0 = (PyArrayObject*) PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    if(dataX0 == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output array - X0");
        goto fail;
    }
    dataY0 = (PyArrayObject*) PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    if(dataY0 == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output array - Y0");
        goto fail;
    }
    dataX1 = (PyArrayObject*) PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    if(dataX1 == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output array - X1");
        goto fail;
    }
    dataY1 = (PyArrayObject*) PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    if(dataY1 == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output array - Y1");
        goto fail;
    }
    
    // Get ready to read in the data section
    float *XY;
    XY = (float *) malloc(sizeof(float)*nSets*header.nFreqs);
    
    // Read in the data section
    buffer = PyObject_CallMethodObjArgs(ph, PyString_FromString("read"), PyInt_FromLong(sizeof(float)*nSets*header.nFreqs), NULL);
    if( buffer == NULL ) {
        if( PyObject_HasAttrString(ph, "read") ) {
            PyErr_Format(PyExc_IOError, "An error occured while reading from the file");
        } else {
            PyErr_Format(PyExc_AttributeError, "Object does not have a read() method");
        }
        goto fail;
    } else if( PyString_GET_SIZE(buffer) != sizeof(float)*nSets*header.nFreqs ) {
        PyErr_Format(eofError, "End of file encountered during filehandle read");
        goto fail;
    }
    memcpy(XY, PyString_AS_STRING(buffer), sizeof(float)*nSets*header.nFreqs);
    Py_XDECREF(buffer);
    
    Py_BEGIN_ALLOW_THREADS
    
    // Fill the data arrays
    float *a, *b, *c, *d;
    a = (float *) PyArray_DATA(dataX0);
    b = (float *) PyArray_DATA(dataY0);
    c = (float *) PyArray_DATA(dataX1);
    d = (float *) PyArray_DATA(dataY1);
    for(i=0; i<header.nFreqs; i++) {
        *(a + i) = *(XY + 0*header.nFreqs + i);
        *(b + i) = *(XY + 1*header.nFreqs + i);
        *(c + i) = *(XY + 2*header.nFreqs + i);
        *(d + i) = *(XY + 3*header.nFreqs + i);
    }
    
    // Clean up the data
    free(XY);
    
    Py_END_ALLOW_THREADS
    
    // Fill in the multi-value fields (tuningWords, fills, errors)
    tuningWords = PyList_New(2);
    if(tuningWords == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output list - tuningWords");
        Py_XDECREF(tuningWords);
        goto fail;
    }
    for(i=0; i<2; i++) {
        temp = Py_BuildValue("I", header.freqCode[i]);
        PyList_SetItem(tuningWords, i, temp);
    }
    
    fills = PyList_New(4);
    if(fills == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output list - fills");
        Py_XDECREF(tuningWords);
        Py_XDECREF(fills);
        goto fail;
    }
    for(i=0; i<4; i++) {
        temp = Py_BuildValue("I", header.fills[i]);
        PyList_SetItem(fills, i, temp);
    }
    
    errors = PyList_New(4);
    if(errors == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output list - flags");
        Py_XDECREF(tuningWords);
        Py_XDECREF(fills);
        Py_XDECREF(errors);
        goto fail;
    }
    for(i=0; i<4; i++) {
        temp = Py_BuildValue("H", header.errors[i]);
        PyList_SetItem(errors, i, temp);
    }
    
    saturations = PyList_New(4);
    if(saturations == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create output list - saturations");
        
        Py_XDECREF(tuningWords);
        Py_XDECREF(fills);
        Py_XDECREF(errors);
        Py_XDECREF(saturations);
        goto fail;
    }
    for(i=0; i<4; i++) {
        temp = Py_BuildValue("H", header.satCount[i]);
        PyList_SetItem(saturations, i, temp);
    }
    
    // Save the data to the frame object
    // 1. Header
    fHeader = PyObject_GetAttrString(frame, "header");
    
    temp = Py_BuildValue("H", header.beam);
    PyObject_SetAttrString(fHeader, "beam", temp);
    Py_XDECREF(temp);
    
    temp = Py_BuildValue("H", header.decFactor);
    PyObject_SetAttrString(fHeader, "decimation", temp);
    Py_XDECREF(temp);
    
    temp = Py_BuildValue("H", header.timeOffset);
    PyObject_SetAttrString(fHeader, "timeOffset", temp);
    Py_XDECREF(temp);
    
    temp = Py_BuildValue("I", header.nInts);
    PyObject_SetAttrString(fHeader, "nInts", temp);
    Py_XDECREF(temp);
    
    // 2. Data
    fData = PyObject_GetAttrString(frame, "data");

    temp = PyLong_FromUnsignedLongLong(header.timeTag0);
    PyObject_SetAttrString(fData, "timeTag", temp);
    Py_XDECREF(temp);

    PyObject_SetAttrString(fData, "tuningWords", tuningWords);
    
    PyObject_SetAttrString(fData, "fills", fills);
    
    PyObject_SetAttrString(fData, "flags", errors);
    
    PyObject_SetAttrString(fData, "saturations", saturations);

    PyObject_SetAttrString(fData, "X0", PyArray_Return(dataX0));
    PyObject_SetAttrString(fData, "Y0", PyArray_Return(dataY0));
    PyObject_SetAttrString(fData, "X1", PyArray_Return(dataX1));
    PyObject_SetAttrString(fData, "Y1", PyArray_Return(dataY1));

    // 3. Frame
    PyObject_SetAttrString(frame, "header", fHeader);
    PyObject_SetAttrString(frame, "data", fData);
    
    Py_XDECREF(fHeader);
    Py_XDECREF(tuningWords);
    Py_XDECREF(fills);
    Py_XDECREF(errors);
    Py_XDECREF(saturations);
    Py_XDECREF(fData);
    Py_XDECREF(dataX0);
    Py_XDECREF(dataY0);
    Py_XDECREF(dataX1);
    Py_XDECREF(dataY1);

    output = Py_BuildValue("O", frame);
    return output;
    
fail:
    Py_XDECREF(buffer);
    Py_XDECREF(dataX0);
    Py_XDECREF(dataX1);
    Py_XDECREF(dataY0);
    Py_XDECREF(dataY1);
    
    return NULL;
}

PyDoc_STRVAR(readDRSpec_doc, \
"Function to read in a DR spectrometer header structure and data and retrun\n\
a drspec.Frame instance.");


/*
Module Setup - Function Definitions and Documentation
*/

static PyMethodDef OldFastMethods[] = {
    {"readDRSpec", (PyCFunction) readDRSpec, METH_VARARGS, readDRSpec_doc},
    {NULL,         NULL,                     0,            NULL}
};

PyDoc_STRVAR(OldFast_doc, "Old Fast! (TM) - DR Spectrometer reader written in C");


/*
Module Setup - Initialization
*/

PyMODINIT_FUNC init_oldfast(void) {
    PyObject *m, *dict1, *dict2;

    // Module definitions and functions
    m = Py_InitModule3("_oldfast", OldFastMethods, OldFast_doc);
    import_array();

    // Exceptions
    
    //   1.  syncError -> similar to lsl.reader.errors.syncError
    dict1 = (PyObject *) PyDict_New();
    if(dict1 == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create exception dictionary");
        Py_XDECREF(dict1);
        Py_XDECREF(m);
    }
    PyDict_SetItemString(dict1, "__doc__", \
        PyString_FromString("Exception raised when a reader encounters an error with one or more of the four sync. words."));
    syncError = PyErr_NewException("_gofast.syncError", PyExc_IOError, dict1);
    Py_INCREF(syncError);
    PyModule_AddObject(m, "syncError", syncError);
    
    //    2. eofError -> similar to lsl.reader.errors.eofError
    dict2 = (PyObject *) PyDict_New();
    if(dict2 == NULL) {
        PyErr_Format(PyExc_MemoryError, "Cannot create exception dictionary");
        Py_XDECREF(dict1);
        Py_XDECREF(syncError);
        Py_XDECREF(dict2);
        Py_XDECREF(m);
    }
    PyDict_SetItemString(dict2, "__doc__", \
        PyString_FromString("Exception raised when a reader encounters the end-of-file while reading."));
    eofError = PyErr_NewException("_gofast.eofError", PyExc_IOError, dict2);
    Py_INCREF(eofError);
    PyModule_AddObject(m, "eofError", eofError);
    
    // Version and revision information
    PyModule_AddObject(m, "__version__", PyString_FromString("0.5"));
    PyModule_AddObject(m, "__revision__", PyString_FromString("$Rev: 2400 $"));
    
}
