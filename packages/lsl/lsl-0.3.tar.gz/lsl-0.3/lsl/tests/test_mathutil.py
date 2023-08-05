# -*- coding: utf-8 -*-

"""Unit test for lsl.misc.mathutil module."""

import unittest
import logging
import math
import StringIO

import numpy

from lsl.misc import mathutil


__revision__  = "$Revision: 88 $"
__version__   = "0.1"
__author__    = "D.L.Wood"
__maintainer__ = "Jayce Dowell"


class mathutil_tests(unittest.TestCase):
	"""A unittest.TestCase collection of unit tests for the lsl.misc.mathutil
	module."""
	
	def setUp(self):
		"""Setup for unit tests."""
		
		# disable logger since we intentionally generate errors 
		logging.basicConfig(stream = StringIO.StringIO())
	
	def test_downsample(self):
		"""Test mathutil.downsample() function."""
		
		x = numpy.array((0, 1, 2, 3))
		
		y = mathutil.downsample(x, 2, False)
		self.assertEqual(len(y), 2)
		self.assertAlmostEqual(y[0], 1.0)
		self.assertAlmostEqual(y[1], 5.0)
		
		y = mathutil.downsample(x, 2, True)
		self.assertEqual(len(y), 2)
		self.assertAlmostEqual(y[0], 0.5)
		self.assertAlmostEqual(y[1], 2.5)
		
		y = mathutil.downsample(x, 3)
		self.assertEqual(len(y), 1)
		self.assertAlmostEqual(y[0], 1.0)
		
	def test_cmagnitde(self):
		"""Test mathutil.cmagnitude() function."""
		
		x = complex(1, 0)
		self.assertAlmostEqual(mathutil.cmagnitude(x), 1.0)
		
		x = complex(0, 1)
		self.assertAlmostEqual(mathutil.cmagnitude(x), 1.0)
		
		x = complex(-1, 0)
		self.assertAlmostEqual(mathutil.cmagnitude(x), 1.0)
		
		x = complex(0, -1)
		self.assertAlmostEqual(mathutil.cmagnitude(x), 1.0)
		
		x = complex(3, 4)
		self.assertAlmostEqual(mathutil.cmagnitude(x), 5.0)
		
	def test_cphase(self):
		"""Test mathutil.cphase() function."""
		
		x = complex(1, 0)
		self.assertAlmostEqual(mathutil.cphase(x), math.radians(0.0))
		
		x = complex(0, 1)
		self.assertAlmostEqual(mathutil.cphase(x), math.radians(90.0))
		
		x = complex(-1, 0)
		self.assertAlmostEqual(mathutil.cphase(x), math.radians(180.0))
		
		x = complex(0, -1)
		self.assertAlmostEqual(mathutil.cphase(x), math.radians(-90.0))
		
	def test_cpolar(self):
		"""Test mathutil.cpolar() function."""
		
		x = numpy.array((0+1j, 1+0j, 1+1j, -1+0j))
		mag = (1.0, 1.0, math.sqrt(2.0), 1.0)
		phase = (math.radians(90.0), 0.0, math.radians(45.0), math.radians(180.0))
		im = iter(mag)
		ip = iter(phase)
		
		pol = mathutil.cpolar(x)
		for p in pol:
			self.assertAlmostEqual(p[0], im.next())
			self.assertAlmostEqual(p[1], ip.next())
			
	def test_creal(self):
		"""Test mathtutil.creal() function."""
		
		x = (1, math.radians(0.0))
		self.assertAlmostEqual(mathutil.creal(x), 1.0)
		
		x = (1, math.radians(90.0))
		self.assertAlmostEqual(mathutil.creal(x), 0.0)
		
		x = (1, math.radians(180.0))
		self.assertAlmostEqual(mathutil.creal(x), -1.0)
		
		x = (1, math.radians(-90.0))
		self.assertAlmostEqual(mathutil.creal(x), 0.0)
			
	def test_cimag(self):
		"""Test mathtutil.cimag() function."""
		
		x = (1, math.radians(0.0))
		self.assertAlmostEqual(mathutil.cimag(x), 0.0)
		
		x = (1, math.radians(90.0))
		self.assertAlmostEqual(mathutil.cimag(x), 1.0)
		
		x = (1, math.radians(180.0))
		self.assertAlmostEqual(mathutil.cimag(x), 0.0)
		
		x = (1, math.radians(-90.0))
		self.assertAlmostEqual(mathutil.cimag(x), -1.0)
		
	def test_crect(self):
		"""Test mathutil.crect() function."""
		
		x = numpy.array(((1.0, math.radians(90.0)),
					(1.0, 0.0),
					(math.sqrt(2.0), math.radians(45.0)),
					(1.0, math.radians(180.0))))
		
		c = (0+1j, 1+0j, 1+1j, -1+0j)
		ic = iter(c)
		
		rect = mathutil.crect(x)
		for r in rect:
			co = ic.next()
			self.assertAlmostEqual(r.real, co.real)
			self.assertAlmostEqual(r.imag, co.imag)
			
	def test_regrid(self):
		"""Test mathutil.regrid() function."""
		
		yout = (0.0, 2.0, 4.0, 6.0, 8.0)
		
		x = numpy.arange(0, 10, dtype = numpy.float_)
		y = numpy.arange(0, 10, dtype = numpy.float_)
		xnew = numpy.arange(0, 10, 2, dtype = numpy.float_)
		
		ynew = mathutil.regrid(x, y, xnew, method = 'spline')
		iy = iter(yout)
		for yn in ynew:
			self.assertAlmostEqual(yn, iy.next())
			
		ynew = mathutil.regrid(x, y, xnew, method = 'linear')
		iy = iter(yout)
		for yn in ynew:
			self.assertAlmostEqual(yn, iy.next())
		
		xnew = numpy.arange(-2, 10, 2, dtype = numpy.float_)    
		self.assertRaises(ValueError, mathutil.regrid, x, y, xnew)
		
		xnew = numpy.arange(0, 12, 2, dtype = numpy.float_)    
		self.assertRaises(ValueError, mathutil.regrid, x, y, xnew)
		
	def test_smooth(self):
		"""Test mathutil.smooth() function."""
		
		x = numpy.arange(0, 100, dtype = numpy.float_)
		mathutil.smooth(x)
		mathutil.smooth(x, window='flat')
		
	def test_to_dB(self):
		"""
		Test mathutil.to_dB() function.
		"""
		
		x = numpy.random.randn(100) + 1000.0
		mathutil.to_dB(x)

	def test_from_dB(self):
		"""Test mathutil.from_dB function."""
		
		x = numpy.arange(1, 100, dtype = numpy.float_)
		mathutil.from_dB(x)
		
	def test_robustmean(self):
		"""Test mathutil.robustmean() function."""
		
		x = numpy.random.randn(100)
		x[0] = 1000.0
		x[-5] = 3000.0
		
		self.assert_(mathutil.robustmean(x) < x.mean())
    
    
class mathutil_test_suite(unittest.TestSuite):
	"""A unittest.TestSuite class which contains all of the lwa_user.mathutil
	module unit tests."""
	
	def __init__(self):
		unittest.TestSuite.__init__(self)
		
		loader = unittest.TestLoader()
		self.addTests(loader.loadTestsFromTestCase(mathutil_tests))        
        
        
if __name__ == '__main__':
	unittest.main()
