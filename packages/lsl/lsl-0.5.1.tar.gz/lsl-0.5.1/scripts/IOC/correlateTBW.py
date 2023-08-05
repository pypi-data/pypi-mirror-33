#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script that reads in TBW data and runs a cross-correlation on it.  
The results are saved in the FITS IDI format.
"""

import os
import sys
import time
import ephem
import numpy
import getopt
import random
from datetime import datetime, timedelta, tzinfo

import lsl.common.metabundle as mcsMB
from lsl import astro
from lsl.common import stations
from lsl.common import dp as dp_common
from lsl.statistics import robust
from lsl.reader import tbw
from lsl.reader import errors
from lsl.correlator import uvUtils
from lsl.correlator import fx as fxc
from lsl.writer import fitsidi

from matplotlib import pyplot as plt


class UTC(tzinfo):
    """tzinfo object for UTC time."""

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


def usage(exitCode=None):
	print """correlateTBW.py - cross-correlate data in a TBW file

Usage: correlateTBW.py [OPTIONS] metaData data

Options:
-h, --help             Display this help information
-f, --fft-length       Set FFT length (default = 512)
-s, --samples          Number of average visibilities to generate
                       (default = 10)
-q, --quiet            Run correlateTBW in silent mode
-x, --xx               Compute only the XX polarization product (default)
-y, --yy               Compute only the YY polarization product
"""

	if exitCode is not None:
		sys.exit(exitCode)
	else:
		return True


def parseConfig(args):
	config = {}
	# Command line flags - default values
	config['LFFT'] = 512
	config['samples'] = 10
	config['offset'] = 0
	config['verbose'] = True
	config['products'] = ['xx',]
	config['args'] = []

	# Read in and process the command line flags
	try:
		opts, arg = getopt.getopt(args, "hql:s:xy", ["help", "quiet", "fft-length=", "samples=", "xx", "yy"])
	except getopt.GetoptError, err:
		# Print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage(exitCode=2)
	
	# Work through opts
	for opt, value in opts:
		if opt in ('-h', '--help'):
			usage(exitCode=0)
		elif opt in ('-q', '--quiet'):
			config['verbose'] = False
		elif opt in ('-l', '--fft-length'):
			config['LFFT'] = int(value)
		elif opt in ('-s', '--samples'):
			config['samples'] = int(value)
		elif opt in ('-x', '--xx'):
			config['products'] = ['xx',]
		elif opt in ('-y', '--yy'):
			config['products'] = ['yy',]
		else:
			assert False
	
	# Add in arguments
	config['args'] = arg

	# Return configuration
	return config


def processChunk(fh, site, good, filename, LFFT=64, Overlap=1, SampleRate=dp_common.fS, ChunkSize=300, pols=['xx',],  dataSize=400):
	"""
	Given a filehandle pointing to some TBW data and various parameters for
	the cross-correlation, write cross-correlate the data and save it to a file.
	"""

	# Get antennas
	antennas = site.getAntennas()

	# Create the list of good digitizers
	goodDigs = []
	dig2ant = {}
	for i in good:
		goodDigs.append(antennas[i].digitizer)
		dig2ant[antennas[i].digitizer] = antennas[i]
	
	# Find out how many frames to work with at a time
	nFrames = int(30000)

	mapper = []
	mapper2 = []
	refTime = 0.0
	setTime = 0.0
	wallTime = time.time()
	for s in xrange(ChunkSize):
		count = {}
		masterCount = 0
		iTime = 0
		data = numpy.zeros((len(good),nFrames*dataSize), dtype=numpy.int16)
		
		i = 0
		j = 0
		while j < (260*nFrames):
			# Read in the next frame and anticipate any problems that could occur
			try:
				cFrame = tbw.readFrame(fh)
			except errors.eofError:
				break
			except errors.syncError:
				#print "WARNING: Mark 5C sync error on frame #%i" % (int(fh.tell())/tbw.FrameSize-1)
				continue

			stand = cFrame.header.parseID()
			pol = 0
			aStand = 2*(stand-1)+pol + 1
				
			if i == 0:
				setTime = cFrame.getTime()
				if s == 0:
					refTime = setTime
				
			if aStand not in goodDigs:
				continue
			
			#if cFrame.header.frameCount % 1000:
				#print "Skipping stand %i -> %i" % (stand, aStand)
				
			oStand = aStand
			if aStand not in mapper:
				mapper.append(aStand)
				mapper2.append(dig2ant[aStand])
				aStand = mapper.index(aStand)
			else:
				aStand = mapper.index(aStand)

			cnt = cFrame.header.frameCount - 1
			data[aStand,  cnt*dataSize:(cnt+1)*dataSize] = cFrame.data.xy[1,:]
			
			masterCount = masterCount + 1
			
			j += 1
		i += 1
		
		setDT = datetime.utcfromtimestamp(setTime)
		setDT.replace(tzinfo=UTC())
		print "Working on set #%i (%.3f seconds after set #1 = %s)" % ((s+1), (setTime-refTime), setDT.strftime("%Y/%m/%d %H:%M:%S.%f"))
		
		nSec = 8
		secSize = data.shape[1]/nSec
		
		for pol in pols:
			print "-> %s" % pol
			try:
				del tempVis
			except:
				pass
			
			for k in xrange(nSec):
				blList, freq, vis = fxc.FXMaster(data[:,k*secSize:(k+1)*secSize], mapper2, LFFT=LFFT, Overlap=Overlap, IncludeAuto=True, verbose=False, SampleRate=SampleRate, Pol=pol, ReturnBaselines=True, GainCorrect=True)

				toUse = numpy.where( (freq>10.0e6) & (freq<88.0e6) )
				toUse = toUse[0]
				
				try:
					tempVis += vis
				except:
					tempVis = vis
					
			vis = tempVis / float(nSec)
			
			if s  == 0 and pol == pols[0]:
				pol1, pol2 = fxc.pol2pol(pol)
				
				fits = fitsidi.IDI(filename, refTime=refTime)
				fits.setStokes(pols)
				fits.setFrequency(freq[toUse])
				fits.setGeometry(site, [a for a in mapper2 if a.pol == pol1])

			obsTime = astro.unix_to_taimjd(setTime)
			fits.addDataSet(obsTime, 512*nFrames/SampleRate, blList, vis[:,toUse], pol=pol)
			print "->  Cummulative Wall Time: %.3f s (%.3f s per integration)" % ((time.time()-wallTime), (time.time()-wallTime)/(s+1))

	fits.write()
	fits.close()
	del(fits)
	del(data)
	del(vis)
	return True


def main(args):
	# Parse command line options
	config = parseConfig(args)
	
	metaDataFile = config['args'][0]
	filename = config['args'][1]

	# Length of the FFT
	LFFT = config['LFFT']

	# First, deal with the metadata
	## Read in the meta-data bundle and split up the data filename into MJD, op 
	## code, etc.
	project = mcsMB.getSessionDefinition(metaDataFile)
	mtch = filenameRE.match('filename')
	
	## Loop over the observation defined in the meta-data bundle and set cObs to 
	## the observation with the right MJD and op code. 
	cObs = None
	for o in project.sessions[0].observations:
		if int(mtch.group('mjd')) == o.mjd and int(mtch.group('opcode')) == o.opcode:
			cObs = o
			break
	if cObs is None:
		print "WARNING:  observation entry for file '%s' not found in '%s'" % (dataFile, metaDataFile)
	
	## Set the station from the meta-data bundle (if it is included) or from the
	## SSMIF supplied with LSL.  
	station = mcsMB.getStation(metaDataFile, ApplySDM=True)
	if station is None:
		print "WARNING:  no SSMIF file found in '%s', using default values" % metaDataFile
		station = stations.lwa1
	antennas = station.getAntennas()

	fh = open(filename, "rb", buffering=tbw.FrameSize*10000)
	test = tbw.readFrame(fh)
	if not test.header.isTBW():
		raise errors.notTBWError()
	fh.seek(0)

	jd = astro.unix_to_utcjd(test.getTime())
	date = str(ephem.Date(jd - astro.DJD_OFFSET))
	sampleRate = dp_common.fS
	nInts = os.path.getsize(filename) / tbw.FrameSize / 30000 / len(antennas) / 2

	# Get valid stands for both polarizations
	goodX = []
	goodY = []
	for i in xrange(len(antennas)):
		ant = antennas[i]
		if ant.stand.id > 255:
			pass
		elif ant.getStatus() != 33:
			pass
		else:
			if ant.pol == 0:
				goodX.append(i)
			else:
				goodY.append(i)
	
	# Select which polarization to use
	if config['products'][0] == 'xx':
		good = goodX
	else:
		good = goodY
		
	# Report on the valid stands found.  This is a little verbose,
	# but nice to see.
	print "Found %i good stands to use" % len(good)
	for i in good:
		print "%3i, %i" % (antennas[i].stand.id, antennas[i].pol)

	# Number of frames to read in at once and average
	nFrames = 30000
	nSets = os.path.getsize(filename) / tbw.FrameSize / 300000

	print "TBW Data:  %s" % test.header.isTBW()
	print "Captures in file: %i (%.3f s)" % (nInts, nInts*30000*400/sampleRate)
	print "=="
	print "Station: %s" % station.name
	print "Date observed: %s" % date
	print "Julian day: %.5f" % jd
	print "Integration Time: %.3f s" % (400*nFrames/sampleRate)
	print "Number of integrations in file: %i" % nSets
	print "=="

	# Align the file with the first full capture
	fh = open(filename, "rb")
	
	i = 0
	junkFrame = tbw.readFrame(fh)
	while not junkFrame.header.isTBW():
		junkFrame = tbw.readFrame(fh)
		i += 1
	fh.seek(-tbw.FrameSize, 1)
	print "Skipped %i non-TBW frames at the beginning of the file" % i

	# Get the data frame size
	dataSize = 400
	if junkFrame.getDataBits() == 4:
		dataSize = 1200
	
	if config['samples'] > nSets:
		config['samples'] = nSets

	s = 0
	leftToDo = config['samples']
	basename, ext = os.path.splitext(filename)
	while leftToDo > 0:
		fitsFilename = "%s.FITS_%i" % (basename, (s+1),)
		
		if leftToDo > 300:
			chunk = 300
		else:
			chunk = leftToDo
		processChunk(fh, station, good, fitsFilename, LFFT=config['LFFT'], Overlap=1, SampleRate=sampleRate,
				ChunkSize=chunk, dataSize=dataSize)

		s = s + 1
		leftToDo = leftToDo - chunk

	fh.close()


if __name__ == "__main__":
	numpy.seterr(all='ignore')
	main(sys.argv[1:])
