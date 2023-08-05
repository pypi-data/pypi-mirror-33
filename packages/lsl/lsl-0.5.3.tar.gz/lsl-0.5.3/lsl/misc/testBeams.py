#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy
from scipy.signal import lfilter
import ephem

from time import time as clock

from lsl.astro import unix_to_utcjd, DJD_OFFSET
from lsl.reader import tbw, errors
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
	dataBits = tbw.getDataBits(fh)
	
	junkFrame = tbw.readFrame(fh)
	fh.seek(0)
	beginTime = junkFrame.getTime()
	beginDate = ephem.Date(unix_to_utcjd(junkFrame.getTime()) - DJD_OFFSET)
	print beginDate
	
	junkFrame = tbw.readFrame(fh)
	while not junkFrame.header.isTBW():
		junkFrame = tbw.readFrame(fh)
	fh.seek(-tbw.FrameSize, 1)
	
	time = numpy.arange(1000500, dtype=numpy.int64)
	data = numpy.zeros((520, time.size), dtype=numpy.int16)
	for j in range(30000*260):
		try:
			cFrame = tbw.readFrame(fh)
		except errors.eofError:
			break
		except errors.syncError:
			print "WARNING: Mark 5C sync error on frame #%i" % (int(fh.tell())/tbw.FrameSize-1)
			continue
		if not cFrame.header.isTBW():
			continue
		
		stand = cFrame.header.parseID()
		aStand = 2*(stand-1)
		count = cFrame.header.frameCount - 1
		try:
			if aStand == 0:
				time[count*400:(count+1)*400] += cFrame.header.timeTag
				time[count*400:(count+1)*400] += numpy.arange(400, dtype=numpy.int64)
			data[aStand,   count*400:(count+1)*400] = cFrame.data.xy[0,:]
			data[aStand+1, count*400:(count+1)*400] = cFrame.data.xy[1,:]
		except:
			pass
	time -= time.min()
	print time
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
			
			dp = SoftwareDP(mode='DRX', filter=7, centralFreq=74.0e6)
			beamX, beamY = beamformer.intDelayAndSum(antennas, data, azimuth=az, elevation=el)
			drxX = dp.apply(time[:len(beamX)], beamX)
			drxY = dp.apply(time[:len(beamY)], beamY)
			
			#drxX = beamX
			#drxY = beamY
			
			print "Az: %.1f, El: %.1f -> X: %.3f dB, Y: %.3f dB" % (az, el, to_dB((abs(drxX)**2).mean()/1e18), to_dB((abs(drxY)**2).mean()/1e18))
			
			outputX[i,j] = (abs(drxX)**2).mean()/1e18
			outputY[i,j] = (abs(drxY)**2).mean()/1e18
			
			print clock() - tStart
			
	import pylab
	pylab.imshow(outputY, interpolation='nearest', origin='lower')
	pylab.show()


if __name__ == "__main__":
	main(sys.argv[1:])
	