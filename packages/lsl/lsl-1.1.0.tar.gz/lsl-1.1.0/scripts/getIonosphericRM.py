#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ephem
import numpy
import getopt
from datetime import datetime

from lsl import astro
from lsl.common.stations import lwa1
from lsl.common.mcs import datetime2mjdmpm
from lsl.misc import ionosphere


def usage(exitCode=None):
	print """getIonosphericRM - Estimate the ionospheric contribution to the RM
for an observation using the IGS final product and the IGRF.

Usage: getIonosphericRM.py [OPTIONS] RA Dec Start Stop

RA:     J2000 right ascension in HH:MM:SS[.SSS]
Dec:    J2000 declination in sDD:MM:SS[.SSS]
Start:  YYYY/MM/DD HH:MM:SS start time in UTC
Stop:   YYYY/MM/DD HH:MM:SS stop time in UTC

Options:
-h, --help             Display this help information
-n, --n-samples        Number of samples to take between the start and stop
                       times (default = 11)
"""

	if exitCode is not None:
		sys.exit(exitCode)
	else:
		return True


def parseConfig(args):
	config = {}
	# Command line flags - default values
	config['nSamples'] = 11
	config['args'] = []
	
	# Read in and process the command line flags
	try:
		opts, arg = getopt.getopt(args, "hn:", ["help", "n-samples"])
	except getopt.GetoptError, err:
		# Print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage(exitCode=2)
	
	# Work through opts
	for opt, value in opts:
		if opt in ('-h', '--help'):
			usage(exitCode=0)
		elif opt in ('-n', '--n-samples'):
			config['nSamples'] = int(value)
		else:
			assert False
	
	# Add in arguments
	config['args'] = arg
	
	# Validate
	if len(config['args']) != 6:
		raise RuntimeError("Invalid number of arguments")
	if config['nSamples'] < 1:
		raise RuntimeError("Invalid number of samples to generate")
		
	# Return configuration
	return config


def main(args):
	# Parse the command line
	config = parseConfig(args)
	
	# Inputs
	RA = ephem.hours( config['args'][0] )
	dec = ephem.degrees( config['args'][1] )
	tStart = "%s %s" % (config['args'][2], config['args'][3])
	tStop = "%s %s" % (config['args'][4], config['args'][5])
	
	# YYYY/MM/DD HH:MM:SS -> datetime instance
	tStart = datetime.strptime(tStart, "%Y/%m/%d %H:%M:%S")
	tStop = datetime.strptime(tStop, "%Y/%m/%d %H:%M:%S")
	
	# datetime instance to MJD
	mjd,mpm = datetime2mjdmpm(tStart)
	mjdStart = mjd + mpm/1000.0/86400.0
	mjd,mpm = datetime2mjdmpm(tStop)
	mjdStop = mjd + mpm/1000.0/86400.0
	
	# Setup everthing for computing the position of the source
	obs = lwa1.getObserver()
	bdy = ephem.FixedBody()
	bdy._ra = RA
	bdy._dec = dec
	
	# Go!
	print "%-13s  %-6s  %-6s  %-21s  %-15s" % ("MJD", "Az.", "El.", "DM [pc/cm^3]", "RM [1/m^2]")
	print "-"*(13+2+6+2+6+2+21+2+15)
	for mjd in numpy.linspace(mjdStart, mjdStop, config['nSamples']):
		# Set the date and compute the location of the target
		obs.date = mjd + astro.MJD_OFFSET - astro.DJD_OFFSET
		bdy.compute(obs)
		az = bdy.az*180/numpy.pi
		el = bdy.alt*180/numpy.pi
		
		if el > 0:
			# Get the latitude, longitude, and height of the ionospheric pierce 
			# point in this direction
			ippLat, ippLon, ippElv = ionosphere.getIonosphericPiercePoint(lwa1, az, el)
			
			# Load in the TEC value and the RMS from the IGS final data product
			tec, rms = ionosphere.getTECValue(mjd, lat=ippLat, lng=ippLon, includeRMS=True, type='IGS')
			tec, rms = tec[0][0], rms[0][0]
			
			# Use the IGRF to compute the ECEF components of the Earth's magnetic field
			Bx, By, Bz = ionosphere.getMagneticField(ippLat, ippLon, ippElv, mjd=mjd, ecef=True)
			
			# Rotate the ECEF field into topocentric coordinates so that we can 
			# get the magnetic field along the line of sight
			rot = numpy.array([[ numpy.sin(lwa1.lat)*numpy.cos(lwa1.long), numpy.sin(lwa1.lat)*numpy.sin(lwa1.long), -numpy.cos(lwa1.lat)], 
						[-numpy.sin(lwa1.long),                     numpy.cos(lwa1.long),                      0                  ],
						[ numpy.cos(lwa1.lat)*numpy.cos(lwa1.long), numpy.cos(lwa1.lat)*numpy.sin(lwa1.long),  numpy.sin(lwa1.lat)]])
			## ECEF -> SEZ
			sez = numpy.dot(rot, numpy.array([Bx, By, Bz]))
			## SEZ -> NEZ
			enz = 1.0*sez[[1,0,2]]
			enz[1] *= -1.0
			
			# Compute the pointing vector for this direction and use that to get
			# B parallel.  Note that we need a negative sign when we dot to get
			# the direction of propagation right.
			pnt = numpy.array([numpy.cos(el*numpy.pi/180)*numpy.sin(az*numpy.pi/180),
						numpy.cos(el*numpy.pi/180)*numpy.cos(az*numpy.pi/180), 
						numpy.sin(el*numpy.pi/180)])
			Bparallel = -numpy.dot(pnt, enz)
			
			# Compute the dispersion measure and the RMS
			DM    = 3.24078e-23 * (tec*1e16)
			rmsDM = 3.24078e-23 * (rms*1e16)
			
			# Compute the rotation measure and the RMS
			RM    = 2.62e-13 * (tec*1e16) * (Bparallel*1e-9)
			rmsRM = 2.62e-13 * (rms*1e16) * (Bparallel*1e-9)
			
			# Report
			print "%013.6f  %6.2f  %6.2f  %8.6f +/- %8.6f  %5.3f +/- %5.3f" % (mjd, az, el, DM, rmsDM, RM, rmsRM)
		else:
			# Write out dummy values since the source isn't up
			print "%013.6f  %6.2f  %6.2f  %8s +/- %8s  %5s +/- %5s" % (mjd, az, el, '---', '---', '---', '---')


if __name__ == "__main__":
	main(sys.argv[1:])
	
