# -*- coding: utf-8 -*-

"""
Module for working with a MCS meta-data tarball and extracting the useful bits out 
it and putting those bits into Python objects, e.g, :class:`lsl.common.stations.LWAStation` 
and :class:`lsl.common.sdm.SDM`.
"""

import os
import re
import glob
import shutil
import tarfile
import tempfile
from datetime import datetime, timedelta

from lsl.common.dp import fS, word2freq
from lsl.common import stations, sdm, sdf
from lsl.common.mcs import *
from lsl.transform import Time

__version__ = '0.3'
__revision__ = '$Rev: 857 $'
__all__ = ['readSESFile', 'readOBSFile', 'readCSFile', 'getSDM', 'getStation', 'getSessionMetaData', 'getSessionSpec', 'getObservationSpec', 'getSessionDefinition', 'getCommandScript', '__version__', '__revision__', '__all__']

# Regular expression for figuring out filenames
filenameRE = re.compile(r'(?P<projectID>[a-zA-Z0-9]{1,8})_(?P<sessionID>\d+)(_(?P<obsID>\d+)(_(?P<obsOutcome>\d+))?)?.*\..*')


def readSESFile(filename):
	"""
	Read in a session specification file (MCS0030, Section 5) and return the data
	as a dictionary.
	"""
	
	# Read the SES
	fh = open(filename, 'rb')

	ses = parseCStruct("""
	unsigned short int FORMAT_VERSION;
	char PROJECT_ID[9];
	unsigned int SESSION_ID;
	unsigned short int SESSION_CRA;
	signed short int SESSION_DRX_BEAM;
	char SESSION_SPC[32];
	unsigned long int SESSION_START_MJD;
	unsigned long int SESSION_START_MPM;
	unsigned long int SESSION_DUR;
	unsigned int SESSION_NOBS;
	signed short int SESSION_MRP_ASP;
	signed short int SESSION_MRP_DP_;
	signed short int SESSION_MRP_DR1;
	signed short int SESSION_MRP_DR2;
	signed short int SESSION_MRP_DR3;
	signed short int SESSION_MRP_DR4;
	signed short int SESSION_MRP_DR5;
	signed short int SESSION_MRP_SHL;
	signed short int SESSION_MRP_MCS;
	signed short int SESSION_MUP_ASP;
	signed short int SESSION_MUP_DP_;
	signed short int SESSION_MUP_DR1;
	signed short int SESSION_MUP_DR2;
	signed short int SESSION_MUP_DR3;
	signed short int SESSION_MUP_DR4;
	signed short int SESSION_MUP_DR5;
	signed short int SESSION_MUP_SHL;
	signed short int SESSION_MUP_MCS;
	signed char SESSION_LOG_SCH;
	signed char SESSION_LOG_EXE;
	signed char SESSION_INC_SMIB;
	signed char SESSION_INC_DES;
	""", endianness='little')

	fh.readinto(ses)
	fh.close()
	
	record = {'ASP': ses.SESSION_MRP_ASP, 'DP_': ses.SESSION_MRP_DP_, 'SHL': ses.SESSION_MRP_SHL, 
			'MCS': ses.SESSION_MRP_MCS, 'DR1': ses.SESSION_MRP_DR1, 'DR2': ses.SESSION_MRP_DR2, 
			'DR3': ses.SESSION_MRP_DR3, 'DR4': ses.SESSION_MRP_DR4, 'DR5': ses.SESSION_MRP_DR5}
	
	update = {'ASP': ses.SESSION_MUP_ASP, 'DP_': ses.SESSION_MUP_DP_, 'SHL': ses.SESSION_MUP_SHL, 
			'MCS': ses.SESSION_MUP_MCS, 'DR1': ses.SESSION_MUP_DR1, 'DR2': ses.SESSION_MUP_DR2, 
			'DR3': ses.SESSION_MUP_DR3, 'DR4': ses.SESSION_MUP_DR4, 'DR5': ses.SESSION_MUP_DR5}
	
	return {'version': ses.FORMAT_VERSION, 'projectID': ses.PROJECT_ID.lstrip().rstrip(), 
		   'sessionID': ses.SESSION_ID,  'CRA': ses.SESSION_CRA,  'drxBeam': ses.SESSION_DRX_BEAM,
		   'spcSetup': ses.SESSION_SPC, 'MJD': ses.SESSION_START_MJD, 'MPM': ses.SESSION_START_MPM, 
		   'Dur': ses.SESSION_DUR, 'nObs': ses.SESSION_NOBS, 'record': record, 'update': update, 
		   'logSch': ses.SESSION_LOG_SCH, 'logExe': ses.SESSION_LOG_EXE, 'incSMIF': ses.SESSION_INC_SMIB,
		   'incDesi': ses.SESSION_INC_DES}


def readOBSFile(filename):
	"""
	Read in a observation specification file (MCS0030, Section 6) and return the
	data as a dictionary.
	"""
	
	# Read the OBS
	fh = open(filename, 'rb')
	
	header = parseCStruct("""
	unsigned short int FORMAT_VERSION;
	char               PROJECT_ID[9];
	unsigned int       SESSION_ID;
	signed short int   SESSION_DRX_BEAM;
	char               SESSION_SPC[32];
	unsigned int       OBS_ID; 
	unsigned long int  OBS_START_MJD;
	unsigned long int  OBS_START_MPM;
	unsigned long int  OBS_DUR;
	unsigned short int OBS_MODE;
	float              OBS_RA;
	float              OBS_DEC;
	unsigned short int OBS_B;
	unsigned int       OBS_FREQ1;
	unsigned int       OBS_FREQ2;
	unsigned short int OBS_BW;
	unsigned int       OBS_STP_N;
	unsigned short int OBS_STP_RADEC;
	""", endianness='little')
	
	fh.readinto(header)

	steps = []
	for n in xrange(header.OBS_STP_N):
		obsStep = parseCStruct("""
		float              OBS_STP_C1;
		float              OBS_STP_C2;
		unsigned int       OBS_STP_T;
		unsigned int       OBS_STP_FREQ1;
		unsigned int       OBS_STP_FREQ2;
		unsigned short int OBS_STP_B;
		""", endianness='little')
		
		fh.readinto(obsStep)
		if obsStep.OBS_STP_B == 3:
			beamBlock = parseCStruct("""
			unsigned short int OBS_BEAM_DELAY[2*LWA_MAX_NSTD];
			signed short int   OBS_BEAM_GAIN[LWA_MAX_NSTD][2][2];
			""", endianness='little')
			
			fh.readinto(beamBlock)
			obsStep.delay = beamBlock.OBS_BEAM_DELAY
			obsStep.gain  = single2multi(beamBlock.OBS_BEAM_GAIN, *beamBlock.dims['OBS_BEAM_GAIN'])
		else:
			obsStep.delay = []
			obsStep.gain  = []
		
		steps.append(obsStep)
		
		alignment = parseCStruct("""
		unsigned int block;
		""", endianness='little')
		
		fh.readinto(alignment)
		
		if alignment.block != (2**32 - 2):
			raise IOError("Bytes alignment lost at bytes %i" % fh.tell())

	footer = parseCStruct("""
	signed short int   OBS_FEE[LWA_MAX_NSTD][2];
	signed short int   OBS_ASP_FLT[LWA_MAX_NSTD];
	signed short int   OBS_ASP_AT1[LWA_MAX_NSTD];
	signed short int   OBS_ASP_AT2[LWA_MAX_NSTD];
	signed short int   OBS_ASP_ATS[LWA_MAX_NSTD];
	unsigned short int OBS_TBW_BITS;
	unsigned int       OBS_TBW_SAMPLES;
	signed short int   OBS_TBN_GAIN;
	signed short int   OBS_DRX_GAIN;
	unsigned int alignment;
	""", endianness='little')
	
	fh.readinto(footer)
	fh.close()
	
	if footer.alignment != (2**32 - 1):
		raise IOError("Bytes alignment lost at bytes %i" % fh.tell())
	
	return {'version': header.FORMAT_VERSION, 'projectID': header.PROJECT_ID.lstrip().rstrip(), 
		   'sessionID': header.SESSION_ID, 'drxBeam': header.SESSION_DRX_BEAM, 
		   'spcSetup': header.SESSION_SPC, 'obsID': header.OBS_ID,
		   'MJD': header.OBS_START_MJD, 'MPM': header.OBS_START_MPM, 'Dur': header.OBS_DUR, 
		   'Mode': header.OBS_MODE, 'RA': header.OBS_RA, 'Dec': header.OBS_DEC, 'Beam': header.OBS_B, 'Freq1': word2freq(header.OBS_FREQ1), 
		   'Freq2': word2freq(header.OBS_FREQ2), 'BW': header.OBS_BW, 'nSteps': header.OBS_STP_N, 
		   'StepRADec': header.OBS_STP_RADEC,  'steps': steps, 
		   'fee': single2multi(footer.OBS_FEE, *footer.dims['OBS_FEE']), 
		   'flt': list(footer.OBS_ASP_FLT), 'at1': list(footer.OBS_ASP_AT1), 
		   'at2': list(footer.OBS_ASP_AT2), 'ats': list(footer.OBS_ASP_ATS), 
		   'tbwBits': footer.OBS_TBW_BITS, 'tbwSamples': footer.OBS_TBW_SAMPLES, 
		   'tbnGain': footer.OBS_TBN_GAIN,  
		   'drxGain': footer.OBS_DRX_GAIN}


def readCSFile(filename):
	"""
	Read in a command script file (MCS0030, currently undocumented) and return the
	data as a list of dictionaries.
	"""
	
	# Read the CS file
	fh = open(filename, 'rb')
	
	commands = []
	while True:
		action = parseCStruct("""
		long int tv[2];
		int bASAP;
		int sid;
		int cid;
		int len;
		""", endianness='little')
		
		try:
			fh.readinto(action)
			
			if action.tv[0] == 0:
				break
			
			if action.len > 0:
				data = parseCStruct("""
				char data[%i];
				""" % action.len, endianness='little')
				
				fh.readinto(data)
				data = data.data
			else:
				data = None
			
			actionPrime = {'time': action.tv[0] + action.tv[1]/1.0e6, 
						'ignoreTime': True if action.bASAP else False, 
						'subsystemID': sid2string(action.sid), 'commandID': cid2string(action.cid), 
						'commandLength': action.len, 'data': data}
						
			commands.append( actionPrime )
		except IOError:
			break
			
	fh.close()
	
	return commands


def getSDM(tarname):
	"""
	Given a MCS meta-data tarball, extract the information stored in the 
	dynamic/sdm.dat file and return a :class:`lsl.common.sdm.SDM` instance
	describing the dynamic condition of the station.
	
	If a sdm.dat file cannot be found in the tarball, None is returned.
	"""
	
	tempDir = tempfile.mkdtemp(prefix='metadata-bundle-')
	
	# Extract the SDM file.  If the dynamic/sdm.dat file cannot be found, None
	# is returned via the try...except block.
	tf = tarfile.open(tarname, mode='r:gz')
	try:
		ti = tf.getmember('dynamic/sdm.dat')
	except KeyError:
		return None
	tf.extractall(path=tempDir, members=[ti,])
	
	# Parse the SDM file and build the SDM instance
	dynamic = sdm.parseSDM(os.path.join(tempDir, 'dynamic', 'sdm.dat'))
	
	# Cleanup
	shutil.rmtree(tempDir, ignore_errors=True)
	
	return dynamic


def getStation(tarname, ApplySDM=True):
	"""
	Given a MCS meta-data tarball, extract the information stored in the ssmif.dat 
	file and return a :class:`lsl.common.stations.LWAStation` object.  Optionally, 
	update the :class:`lsl.common.stations.Antenna` instances associated whith the
	LWAStation object using the included SDM file.
	
	If a ssmif.dat file cannot be found in the tarball, None is returned.  
	"""
	
	tempDir = tempfile.mkdtemp(prefix='metadata-bundle-')
	
	# Extract the SSMIF and SDM files.  If the ssmif.dat file cannot be found, None
	# is returned via the try...except block
	tf = tarfile.open(tarname, mode='r:gz')
	try:
		ti = tf.getmember('ssmif.dat')
	except KeyError:
		return None
	tf.extractall(path=tempDir, members=[ti,])
	
	# Read in the SSMIF
	station = stations.parseSSMIF(os.path.join(tempDir, 'ssmif.dat'))
	
	# Get the SDM (if we need to)
	if ApplySDM:
		dynamic = getSDM(tarname)
	else:
		dynamic = None
	
	# Update the SSMIF entries
	if dynamic is not None:
		newAnts = dynamic.updateAntennas(station.getAntennas())
		station.antennas = newAnts
	
	# Cleanup
	shutil.rmtree(tempDir, ignore_errors=True)
	
	# Return
	return station


def getSessionMetaData(tarname):
	"""
	Given a MCS meta-data tarball, extract the session meta-data file (MCS0030, 
	Section 7) and return a dictionary of observations that contain dictionaries 
	of the OP_TAG (tag), OBS_OUTCOME (outcome), and the MSG (msg).
	"""
	
	tempDir = tempfile.mkdtemp(prefix='metadata-bundle-')
	path, basename = os.path.split(tarname)
	basename, ext = os.path.splitext(basename)
	
	# Extract the session meta-data file (_metadata.txt)
	tf = tarfile.open(tarname, mode='r:gz')
	try:
		ti = tf.getmember('%s_metadata.txt' % basename)
	except KeyError:
		for ti in tf.getmembers():
			if ti.name[-13:] == '_metadata.txt':
				break
	tf.extractall(path=tempDir, members=[ti,])
	
	# Read in the SMF
	filename = os.path.join(tempDir, ti.name)
	fh = open(filename, 'r')

	result = {}
	for line in fh:
		line = line.replace('\n', '')
		if len(line) == 0:
			continue

		## I don't really know how the messages will look so we use this try...except
		## block should take care of the various situations.
		try:
			obsID, opTag, obsOutcome, msg = line.split(None, 3)
		except ValueError:
			try:
				obsID, opTag, obsOutcome = line.split(None, 2)
				msg = ''
			except ValueError:
				obsID, obsOutcome = line.split(None, 1)
				opTag = '-1'
				msg = ''

		obsID = int(obsID)
		obsOutcome = int(obsOutcome)
		result[obsID] = {'tag': opTag, 'outcome': obsOutcome, 'msg': msg}
		
	fh.close()
	
	# Cleanup
	shutil.rmtree(tempDir, ignore_errors=True)
	
	# Return
	return result


def getSessionSpec(tarname):
	"""
	Given a MCS meta-data tarball, extract the session specification file (MCS0030, 
	Section 5) and return a dictionary of parameters.
	"""
	
	tempDir = tempfile.mkdtemp(prefix='metadata-bundle-')
	path, basename = os.path.split(tarname)
	basename, ext = os.path.splitext(basename)
	
	# Extract the session specification file (.ses)
	tf = tarfile.open(tarname, mode='r:gz')
	try:
		ti = tf.getmember('%s.ses' % basename)
	except KeyError:
		for ti in tf.getmembers():
			if ti.name[-4:] == '.ses':
				break
	tf.extractall(path=tempDir, members=[ti,])
	
	# Read in the SES
	ses = readSESFile(os.path.join(tempDir, ti.name))
	
	# Cleanup
	shutil.rmtree(tempDir, ignore_errors=True)
	
	# Return
	return ses


def getObservationSpec(tarname, selectObs=None):
	"""
	Given a MCS meta-data tarball, extract one or more observation specification 
	file (MCS0030, Section 6) and return a list of dictionaries corresponding to
	each OBS file.  If the `selectObs` keyword is set to a list of observation
	numbers, only observations matching the numbers in `selectObs` are returned.
	"""
	
	tempDir = tempfile.mkdtemp(prefix='metadata-bundle-')
	path, basename = os.path.split(tarname)
	basename, ext = os.path.splitext(basename)
	
	# Find all of the .obs files and extract them
	tf = tarfile.open(tarname, mode='r:gz')
	tis = []
	for ti in tf.getmembers():
		if ti.name[-4:] == '.obs':
			tis.append(ti)
	tf.extractall(path=tempDir, members=tis)
	
	# Read in the OBS files
	obsList = []
	for of in sorted(glob.glob(os.path.join(tempDir, '*.obs'))):
		obsList.append( readOBSFile(of) )
		
	# Cull the list based on the observation ID selection
	if selectObs is not None:
		outObs = []
		for o in obsList:
			try:
				if o['obsID'] in selectObs:
					outObs.append(o)
			except TypeError:
				if o['obsID'] == selectObs:
					outObs.append(o)
					
		if len(outObs) == 1:
			outObs = outObs[0]
	else:
		outObs = obsList
		
	# Cleanup
	shutil.rmtree(tempDir, ignore_errors=True)
	
	# Return
	return outObs


def getSessionDefinition(tarname):
	"""
	Given a MCS meta-data tarball, extract the session specification file, the 
	session meta-data file, and all observation specification files to build up
	a SDF-representation of the session.
	
	.. note::
		This function returns a full :class:`lsl.common.sdf.Project` instance 
		with the session in question stored under `project.sessions[0]` and the 
		observations under `project.sessions[0].observations`.
	"""
	
	# Find the SDF file contained in the tarball
	tempDir = tempfile.mkdtemp(prefix='metadata-bundle-')
	path, basename = os.path.split(tarname)
	basename, ext = os.path.splitext(basename)
	
	# Find the right .txt file (not the metadata one) and extract it
	tf = tarfile.open(tarname, mode='r:gz')
	for ti in tf.getmembers():
		if ti.name[-4:] == '.txt' and ti.name.find('metadata') == -1:
			break
	tf.extractall(path=tempDir, members=[ti,])
	
	# Parse it
	project = sdf.parseSDF(os.path.join(tempDir, ti.name))
	
	# Clean up
	shutil.rmtree(tempDir, ignore_errors=True)
	
	# Return the filled-in SDF instance
	return project


def getCommandScript(tarname):
	"""
	Given a MCS meta-data tarball, extract the command script and parse it.  The
	commands are returned as a list of dictionaries (one dictionary per command).
	"""
	
	tempDir = tempfile.mkdtemp(prefix='metadata-bundle-')
	path, basename = os.path.split(tarname)
	basename, ext = os.path.splitext(basename)
	
	# Find the .cs file and extract it
	tf = tarfile.open(tarname, mode='r:gz')
	for ti in tf.getmembers():
		if ti.name[-3:] == '.cs':
			break
	tf.extractall(path=tempDir, members=[ti,])
	
	# Read in the CS
	cs = readCSFile(os.path.join(tempDir, ti.name))
	
	# Cleanup
	shutil.rmtree(tempDir, ignore_errors=True)
	
	# Return
	return cs
