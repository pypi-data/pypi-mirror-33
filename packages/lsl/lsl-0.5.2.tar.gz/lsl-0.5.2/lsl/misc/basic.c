#include "Python.h"
#include <math.h>
#include <stdio.h>
#include <cblas.h>
#include <fftw3.h>
#include <stdlib.h>
#include <complex.h>

#ifdef _OPENMP
	#include <omp.h>
#endif

#include "numpy/arrayobject.h"

#define PI 3.1415926535898
#define imaginary _Complex_I


static PyObject *IntegerDelayAndSum(PyObject *self, PyObject *args, PyObject *kwds) {
	PyObject *antennas, *signals, *delays, *antenna, *pol, *output;
	PyArrayObject *data, *delay, *dataF;
	
	long i, j, k, m, nStand, nSamps, maxDelay;
	
	if(!PyArg_ParseTuple(args, "OOO", &antennas, &signals, &delays)) {
		PyErr_Format(PyExc_RuntimeError, "Invalid parameters");
		return NULL;
	}
	
	// Bring the data into C and make it usable
	data  = (PyArrayObject *) PyArray_ContiguousFromObject(signals, NPY_INT16, 2, 2);
	delay = (PyArrayObject *) PyArray_ContiguousFromObject(delays, NPY_INT16, 1, 1);
	
	// Check data dimensions
	if((long) PyList_Size(antennas) != data->dimensions[0]) {
		PyErr_Format(PyExc_TypeError, "signals and coefficients have different stand counts");
		Py_XDECREF(data);
		Py_XDECREF(delay);
		return NULL;
	}
	if(data->dimensions[0] != delay->dimensions[0]) {
		PyErr_Format(PyExc_TypeError, "signals and sample delays have different stand counts");
		Py_XDECREF(data);
		Py_XDECREF(delay);
		return NULL;
	}
	
	// Get channel count and number of FFTs stored
	nStand = (long) data->dimensions[0];
	nSamps = (long) data->dimensions[1];
	
	short int *b;
	b = (short int *) delay->data;
	maxDelay = 0;
	for(i=0; i<nStand; i++) {
		if( *(b + i) > maxDelay ) {
			maxDelay = (long) *(b + i);
		}
	}
	
	// Create the output beam and partial sum holders
	npy_intp dims[2];
	dims[0] = (npy_intp) 2;
	dims[1] = (npy_intp) (nSamps - maxDelay);
	dataF = (PyArrayObject*) PyArray_SimpleNew(2, dims, NPY_FLOAT32);
	if(dataF == NULL) {
		PyErr_Format(PyExc_MemoryError, "Cannot create output array");
		Py_XDECREF(data);
		Py_XDECREF(delay);
		Py_XDECREF(dataF);
		return NULL;
	}
	PyArray_FILLWBYTE(dataF, 0);
	
	// Get the list of polarizations
	short int *p;
	p = (short int *) malloc(nStand * sizeof(short int));
	for(i=0; i<nStand; i++) {
		antenna = PyList_GetItem(antennas, i);
		pol = PyObject_GetAttrString(antenna, "pol");
		*(p + i) = (short int) PyInt_AsLong(pol);
		Py_XDECREF(pol);
	}
	
	short int *a;
	float *c;
	a = (short int *) data->data;
	c = (float *) dataF->data;
	
	float tempX, tempY;
	printf("Here\n");
	
	#ifdef _OPENMP
		#pragma omp parallel default(shared) private(j, k, tempX, tempY)
	#endif
	{
		#ifdef _OPENMP
			#pragma omp for schedule(guided)
		#endif
		for(i=0; i<(nSamps - maxDelay - 1); i++) {
			tempX = 0.0;
			tempY = 0.0;
			
			// Apply the beamform coeffieients to the data and sum over inputs
			for(j=0; j<nStand; j++) {
				tempX += (float) *(a + nSamps*j + i + *(b + j)) * (1 - *(p + j));
				tempY += (float) *(a + nSamps*j + i + *(b + j)) * *(p + j);
			}
			
			// Apply the partial sum to the full beam
			*(c + nSamps*0 + i) = tempX;
			*(c + nSamps*1 + i) = tempY;
		}
	}
	Py_XDECREF(data);
	Py_XDECREF(delay);
	free(p);
	printf("There\n");
	
	output = Py_BuildValue("O", PyArray_Return(dataF));
	Py_XDECREF(dataF);

	return output;
}

PyDoc_STRVAR(IntegerDelayAndSum_doc, \
"Given a list on antenna instances, a 2-D (stands by samples) numpy.int16\n\
data array and a set of numpy.int16 sample delays, beamform the data.\n\
\n\
Input arguments are:\n\
 * antennas: List of antennas instances for each input signal\n\
 * signals: 2-D numpy.int16 (stands by samples) array of data to beamform\n\
 * delays: 1-D numpy.int16 array of sample delays\n\
\n\
Outputs:\n\
  * The beam as a 2-D numpy.float32 (polarizations by samples) array\n\
");


static PyObject *PhaseAndSum(PyObject *self, PyObject *args, PyObject *kwds) {
	PyObject *antennas, *signals, *beam, *antenna, *pol, *output;
	PyArrayObject *data, *coeff, *dataF;
	
	long i, j, k, m, nStand, nSamps;
	
	if(!PyArg_ParseTuple(args, "OOO", &antennas, &signals, &beam)) {
		PyErr_Format(PyExc_RuntimeError, "Invalid parameters");
		return NULL;
	}

	// Bring the data into C and make it usable
	data  = (PyArrayObject *) PyArray_ContiguousFromObject(signals, NPY_COMPLEX64, 2, 2);
	coeff = (PyArrayObject *) PyArray_ContiguousFromObject(beam, NPY_COMPLEX64, 1, 1);
	
	// Check data dimensions
	if((long) PyList_Size(antennas) != data->dimensions[0]) {
		PyErr_Format(PyExc_TypeError, "signals and coefficients have different stand counts");
		Py_XDECREF(data);
		Py_XDECREF(coeff);
		return NULL;
	}
	
	if(data->dimensions[0] != coeff->dimensions[0]) {
		PyErr_Format(PyExc_TypeError, "signals and coefficients have different stand counts");
		Py_XDECREF(data);
		Py_XDECREF(coeff);
		return NULL;
	}
	
	// Get channel count and number of FFTs stored
	nStand = (long) data->dimensions[0];
	nSamps = (long) data->dimensions[1];
	
	// Create the output beam and partial sum holders
	npy_intp dims[2];
	dims[0] = (npy_intp) 2;
	dims[1] = (npy_intp) nSamps;
	dataF = (PyArrayObject*) PyArray_SimpleNew(2, dims, NPY_COMPLEX64);
	if(dataF == NULL) {
		PyErr_Format(PyExc_MemoryError, "Cannot create output array");
		Py_XDECREF(data);
		Py_XDECREF(coeff);
		Py_XDECREF(dataF);
		return NULL;
	}
	PyArray_FILLWBYTE(dataF, 0);
	
	float complex *a, *b, *c;
	a = (float complex *) data->data;
	b = (float complex *) coeff->data;
	c = (float complex *) dataF->data;
	
	// Get the list of polarizations
	short int *p;
	p = (short int *) malloc(nStand * sizeof(short int));
	for(i=0; i<nStand; i++) {
		antenna = PyList_GetItem(antennas, i);
		pol = PyObject_GetAttrString(antenna, "pol");
		*(p + i) = (short int) PyInt_AsLong(pol);
		Py_XDECREF(pol);
	}
	
	float complex tempX, tempY;
	
	#ifdef _OPENMP
		#pragma omp parallel default(shared) private(j, tempX, tempY)
	#endif
	{
		#ifdef _OPENMP
			#pragma omp for schedule(guided)
		#endif
		for(i=0; i<nSamps; i++) {
			tempX = 0.0;
			tempY = 0.0;
			
			// Apply the beamform coeffieients to the data and sum over inputs
			for(j=0; j<nStand; j++) {
				*(c + nSamps*0 + i) += (*(a + nSamps*j + i) * *(b + j)) * (1 - *(p+j));
				*(c + nSamps*1 + i) += (*(a + nSamps*j + i) * *(b + j)) * *(p+j);
			}
			
			// Apply the partial sum to the full beam
			*(c + nSamps*0 + i) = tempX;
			*(c + nSamps*1 + i) = tempY;
		}
	}
	Py_XDECREF(data);
	Py_XDECREF(coeff);
	free(p);
	
	output = Py_BuildValue("O", PyArray_Return(dataF));
	Py_XDECREF(dataF);

	return output;
}

PyDoc_STRVAR(PhaseAndSum_doc, \
"Given a list on antenna instances, a 2-D (stands by samples) numpy.complex64\n\
data array and a set of numpy.complex64 phase-and-sum beamforming coefficients,\n\
beamform the data.\n\
\n\
Input arguments are:\n\
 * antennas: List of antennas instances for each input signal\n\
 * signals: 2-D numpy.complex64 (stands by samples) array of data to\n\
   beamform\n\
 * coefficients: 1-D numpy.complex64 array of phase-and-sum beamforming\n\
   coefficients\n\
\n\
Outputs:\n\
  * The beam as a 2-D numpy.complex64 (polarizations by samples) array\n\
");


static PyMethodDef BasicMethods[] = {
	{"IntegerDelayAndSum", IntegerDelayAndSum, METH_VARARGS, IntegerDelayAndSum_doc }, 
	{"PhaseAndSum",        PhaseAndSum,        METH_VARARGS, PhaseAndSum_doc        }, 
	{NULL,                 NULL,               0,            NULL                   }
};

PyDoc_STRVAR(BasicMethods_doc, \
"C-based module for phase-and-sum beamforming of TBN data.  The methods in\n\
this module are:\n\
  * IntegerDelayAndSum - Form one beam from TBW data\n\
  * PhaseAndSum - Form one beam from TBN data\n\
");


/*
  Module Setup - Initialization
*/

PyMODINIT_FUNC init_basic(void) {
	PyObject *m;

	// Module definitions and functions
	m = Py_InitModule3("_basic", BasicMethods, BasicMethods_doc);
	import_array();
	
	// Version and revision information
	PyModule_AddObject(m, "__version__", PyString_FromString("0.1"));
	PyModule_AddObject(m, "__revision__", PyString_FromString("$Rev$"));
	
}

