#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy
from scipy.signal import lfilter
import ephem

from time import time as clock

from lsl.astro import unix_to_utcjd, DJD_OFFSET
from lsl.reader import tbn, errors
from lsl.reader.buffer import TBNFrameBuffer
from lsl.misc.mathutil import to_dB
from lsl.common.stations import lwa1
import beamformer
from lsl.common.dp import SoftwareDP


def main(args):
	antennas = lwa1.getAntennas()
	
	#
	# Begin TBW Data
	#
	filename = args[0]
	fh = open(filename, 'rb')
	
	junkFrame = tbn.readFrame(fh)
	sampleRate = tbn.getSampleRate(fh)
	fh.seek(0)
	beginTime = junkFrame.getTime()
	beginDate = ephem.Date(unix_to_utcjd(junkFrame.getTime()) - DJD_OFFSET)
	centralFreq = junkFrame.getCentralFreq()
	print beginDate, centralFreq, sampleRate
	
	# Go!
	framesWork = 101563
	buffer = TBNFrameBuffer(stands=range(1,520/2+1), pols=[0, 1], ReorderFrames=False)
	data = numpy.zeros((520, framesWork/520*512), dtype=numpy.complex64)
	count = [0 for a in xrange(520)]
		
	j = 0
	fillsWork = framesWork / 520
	# Inner loop that actually reads the frames into the data array
	while j < fillsWork:
		try:
			cFrame = tbn.readFrame(fh)
		except errors.eofError:
			break
		except errors.syncError:
			#print "WARNING: Mark 5C sync error on frame #%i" % (int(fh.tell())/tbn.FrameSize-1)
			continue
				
		buffer.append(cFrame)
		cFrames = buffer.get()

		if cFrames is None:
			continue
		
		valid = reduce(lambda x,y: x+int(y.valid), cFrames, 0)
		if valid != 520:
			print "WARNING: frame count %i at %i missing %.2f%% of frames" % (cFrames[0].header.frameCount, cFrames[0].data.timeTag, float(520 - valid)/520*100)
			continue
		
		for cFrame in cFrames:
			stand,pol = cFrame.header.parseID()
			
			# In the current configuration, stands start at 1 and go up to 260.  So, we
			# can use this little trick to populate the data array
			aStand = 2*(stand-1)+pol
			
			data[aStand, count[aStand]*512:(count[aStand]+1)*512] = cFrame.data.iq
			
			# Update the counters so that we can average properly later on
			count[aStand] = count[aStand] + 1
			
		j += 1
	#
	# End TBW Data
	#
	
	import aipy
	fake = aipy.img.ImgW(size=40, res=0.5)
	xyz = fake.get_top(center=(40,40))
	azs, alts = aipy.coord.top2azalt(xyz)
	outputX = 0.0*azs
	outputY = 0.0*alts
	print outputX.shape
	
	for i in xrange(outputX.shape[0]):
		#az = i + 294
		for j in xrange(outputX.shape[1]):
			tStart = clock()
			
			az = azs[i,j]*180/numpy.pi
			el = alts[i,j]*180/numpy.pi
			if not numpy.isfinite(az) or not numpy.isfinite(el):
				continue
			
			beamX, beamY = beamformer.phaseAndSum(antennas, data, sampleRate=sampleRate, CentralFreq=centralFreq, azimuth=az, elevation=el)
			tbnX = beamX
			tbnY = beamY
			
			print "Az: %.1f, El: %.1f -> X: %.3f dB, Y: %.3f dB" % (az, el, to_dB((abs(tbnX)**2).mean()/1e3), to_dB((abs(tbnY)**2).mean()/1e3))
			
			outputX[i,j] = (abs(tbnX)**2).mean()/1e3
			outputY[i,j] = (abs(tbnY)**2).mean()/1e3
			
			print clock() - tStart
			
	import pylab
	pylab.imshow(outputY, interpolation='nearest', origin='lower')
	pylab.show()


if __name__ == "__main__":
	main(sys.argv[1:])
	