#!/usr/bin/env python

from lsl.common import metabundle


a = metabundle.getCommandScript('metadata.tgz')
print len(a)
for b in a:
	print b

nBAM = 0
for b in a:
	if b['commandID'] == 'BAM':
		nBAM += 1
print nBAM



a = metabundle.getSessionSpec('metadata.tgz')
print a

a = metabundle.getObservationSpec('metadata.tgz')
print a
a = metabundle.getObservationSpec('metadata.tgz', selectObs=1)
print a

a = metabundle.getSessionMetaData('metadata.tgz')
print a
