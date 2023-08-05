#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pyfits

hdulist = pyfits.open(sys.argv[1])
print hdulist[1].header

n = 0
for row in hdulist[1].data:
	print row['SCAN'], row['BEAM'], row['IF'], row['CRPIX1'], row['CRVAL1'], row['CDELT1'], row['DATA'].shape, row['DATA'].mean()
	n += 1
print n

print len(hdulist)
hdulist.close()
