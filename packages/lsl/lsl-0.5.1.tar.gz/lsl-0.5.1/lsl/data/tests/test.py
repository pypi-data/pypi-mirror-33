#!/usr/bin/env python

from lsl.reader import drspec

fh = open('drspec-test.dat')
for i in xrange(1,8):
	frame = drspec.readFrame(fh)
	print i, frame.parseID(), frame.getSampleRate(), frame.getFilterCode()
drspec.readFrame(fh)
fh.close()

