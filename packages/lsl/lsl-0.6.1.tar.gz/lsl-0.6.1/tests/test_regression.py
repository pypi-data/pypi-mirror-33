# -*- coding: utf-8 -*-

"""Unit test for regressions in LSL"""

import os
import numpy
import unittest

__revision__ = "$ Revision: 1 $"
__version__  = "0.1"
__author__    = "Jayce Dowell"


class regression_tests(unittest.TestCase):
	"""A unittest.TestCase collection of unit tests for the regressions in LSL."""
	
	def test_difxconfig(self):
		"""Test for syntax errors in misc.difxconfig"""
		
		from lsl.misc import difxconfig


class regression_test_suite(unittest.TestSuite):
	"""A unittest.TestSuite class which contains all of the regression unit tests."""
	
	def __init__(self):
		unittest.TestSuite.__init__(self)
		
		loader = unittest.TestLoader()
		self.addTests(loader.loadTestsFromTestCase(regression_tests)) 


if __name__ == '__main__':
	unittest.main()

