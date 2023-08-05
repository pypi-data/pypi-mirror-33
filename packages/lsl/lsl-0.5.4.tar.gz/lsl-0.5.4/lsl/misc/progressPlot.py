#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy
import aipy

from lsl.statistics import robust

from matplotlib import pyplot as plt


az = []
el = []
px = []
py = []

fh = open(sys.argv[1], 'r')
for line in fh:
	line = line.replace(',', '')
	if line[:2] != 'Az':
		continue

	fields = line.split()
	az.append(float(fields[1]))
	el.append(float(fields[3]))
	px.append(10**(float(fields[6])/10))
	py.append(10**(float(fields[9])/10))
fh.close()

fake = aipy.img.ImgW(size=40, res=0.5)
xyz = fake.get_top(center=(40,40))
azs, alts = aipy.coord.top2azalt(xyz)
outputX = 0.0*azs
outputY = 0.0*alts


for a,e,x,y in zip(az,el,px,py):
	d = (a*numpy.pi/180-azs.data)**2 + (e*numpy.pi/180-alts.data)**2

	best = numpy.where( d == d.min() )
	outputX[best] = x
	outputY[best] = y


sx = robust.mean(numpy.array(px))
sy = robust.mean(numpy.array(py))

bad = numpy.where( outputX.data == 0 )
outputX[bad] = sx
outputY[bad] = sy


fig = plt.figure()
axX = fig.add_subplot(2, 1, 1)
axY = fig.add_subplot(2, 1, 2)
axX.imshow(outputX, origin='lower', interpolation='nearest')
axY.imshow(outputY, origin='lower', interpolation='nearest')
plt.show()
