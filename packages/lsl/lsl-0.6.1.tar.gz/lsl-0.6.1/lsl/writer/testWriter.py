#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy

from lsl import astro
from lsl.common.stations import lwa1, Antenna

import sdfits2

nAnt = 20
nChan = 2048
refTime = time.time()


fits = sdfits2.SD('test.fits', refTime=refTime)
fits.setSite(lwa1)
fits.setStokes(['XX', 'YY'])
fits.setFrequency(numpy.linspace(74e6, 84e6, nChan-1))
fits.setObserver('Jayce Dowell', project='Test Project', mode='TBW')

beams = []
for i in xrange(nAnt):
	beams.append(Antenna(i/2+1, pol=i%2))

for i in xrange(15):
	print i
	
	intTime = 5.0
	setTime = refTime + intTime*i
	
	obsTime = astro.unix_to_taimjd(setTime)
	data = numpy.random.rand(nAnt, nChan-1)
	data = data.astype(numpy.float32)
	print data[0::2,:].mean()
	for j in xrange(nAnt/2):
		print j, j+1
		data[2*j+0,:] += (j+1)
		data[2*j+1,:] -= (j+2)
	print data[0::2,:].mean()
	
	fits.addDataSet(obsTime, intTime, beams[0::2], data[0::2,:], pol='XX')
	fits.addDataSet(obsTime, intTime, beams[0::2], data[1::2,:], pol='YY')
	
fits.write()
fits.close()
