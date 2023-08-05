#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import sdm
import metabundle
import stations

import struct
from binascii import unhexlify

def decodeDRX(cmd):
	"""
	Given a hexadecimal string for a DRX command, break it into its various 
	components.  Returns a dictionary of:
	  * Beam
	  * Tuning
	  * Frequency (in Hz)
	  * BW code
	  * Gain
	  * Subslot
	"""
	
	cmd = unhexlify(cmd)
	fields = struct.unpack(">BBfBHB", cmd)
        
	return {'Beam': fields[0], 'Tuning': fields[1], 
		   'Freq': fields[2], 'BW': fields[3], 
		   'Gain': fields[4], 'Subslot': fields[5]}


def decodeBAM(cmnd):
	"""
	Given a hexadecimal string for a BAM command, break it into its various 
	components.  Returns a dictionary of:
	  * Beam
	  * Delays (520)
	  * Gains (260 by 2 by 2)
	  * Subslot
	"""
	
	cmd = unhexlify(cmd)
	fields = struct.unpack(">h520H1040HB", cmd)
	
	return {'Beam': fields[0], 'Delays': fields[1:521], 
		   'Gains': fields[521:1562], 'Subslot': fields[1562]}

filename = sys.argv[1]
print filename

for c in metabundle.getCommandScript(filename):
	if c['commandID'] == 'DRX':
		print decodeDRX(c['data'])
