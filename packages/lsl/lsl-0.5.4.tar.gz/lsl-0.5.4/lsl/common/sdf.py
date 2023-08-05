# -*- coding: utf-8 -*-

"""
Module that contains all of the relevant class to build up a representation 
of a session definition file as defined in MCS0030v5.  The hierarchy of classes
is:
  * Project - class that holds all of the information about the project (including
    the observer) and one or more sessions.  Technically, a SD file has only one
    session but this approach allows for the generation of multiple SD files from
    on Project object.
  * Observer - class that hold the observer's name and numeric ID
  * Session - class that holds all of the observations associated with a particular 
    DP output.  
  * Observations - class that hold information about a particular observation.  It
    includes a variety of attributes that are used to convert human-readable inputs
    to SDF data values.  The observation class is further subclasses into:
    - TBW - class for TBW observations
    - TBN - class for TBN observations
    - DRX - class for general DRX observation, with sub-classes:
      * Solar - class for solar tracking
      * Jovian - class for Jovian tracking
    - Stepped - class for stepped observations
  * BeamStep - class that holds the information about a particular step in a Stepped
    Observation
    
All of the classes, except for Stepped and BeamStep, are complete and functional.  In 
addition, most class contain 'validate' attribute functions that can be used to 
determine if the project/session/observation are valid or not given the constraints of
the DP system.

In addition to providing the means for creating session definition files from scratch, 
this module also includes a simple parser for SD file.  It is mostly complete but does
not currently support some of the extended session/observation parameters.
  
Also included as part of this module are utilities to convert delays (in ns) and gains
into the data formated expected by DP and required for MCS0030v5
"""

import os
import re
import copy
import math
import pytz
import ephem
from datetime import datetime, timedelta

from jinja2 import Template

from lsl.transform import Time
from lsl.astro import MJD_OFFSET, DJD_OFFSET

from lsl.common.dp import freq2word, word2freq
from lsl.common.stations import lwa1
from lsl.reader.tbn import filterCodes as TBNFilters
from lsl.reader.drx import filterCodes as DRXFilters
from lsl.reader.tbw import FrameSize as TBWSize
from lsl.reader.tbn import FrameSize as TBNSize
from lsl.reader.drx import FrameSize as DRXSize


__version__ = '0.8'
__revision__ = '$Rev: 998 $'
__all__ = ['Observer', 'ProjectOffice', 'Project', 'Session', 'Observation', 'TBW', 'TBN', 'DRX', 'Solar', 'Jovian', 'Stepped', 'BeamStep', 'parseSDF',  '__version__', '__revision__', '__all__']

_dtRE = re.compile(r'^((?P<tz>[A-Z]{2,3}) )?(?P<year>\d{4})[ -/]((?P<month>\d{1,2})|(?P<mname>[A-Za-z]{3}))[ -/](?P<day>\d{1,2})[ T](?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}(\.\d{1,6})?)$')
_UTC = pytz.utc
_EST = pytz.timezone('US/Eastern')
_CST = pytz.timezone('US/Central')
_MST = pytz.timezone('US/Mountain')
_PST = pytz.timezone('US/Pacific')
_nStands = 260
_DRSUCapacityTB = 10
# Factors for computing the time it takes to read out a TBW from the number 
# of samples
_TBW_TIME_SCALE = 196000
_TBW_TIME_GAIN = 5000


def _getEquinoxEquation(jd):
	"""
	Compute the equation of the equinoxes (nutation in right ascension) in 
	hours for the specified Julian Date.
	
	From:
	http://aa.usno.navy.mil/faq/docs/GAST.php
	"""
	
	# Get the number of days since January 1, 2000 @ 12:00 UT
	D = jd - 2451545.0

	# Compute the obliquity
	epsilon = 23.4393 - 0.0000004*D
	
	# Compute the mean longitude of the Sun
	L = 280.47 + 0.98565*D
	
	# Compute the longitude of the Moon's ascending node
	Omega = 125.04 - 0.052954*D
	
	# The nutation in the longitude (hours)
	deltaPsi = -0.000319*math.sin(Omega*math.pi/180) - 0.000024*math.sin(2*L*math.pi/180)

	# Return the equation of the equinoxes
	return deltaPsi * math.cos(epsilon*math.pi/180.0)


def parseTimeString(s):
	"""Given a string in the format of (UTC) YYYY MM DD HH:MM:SS.SSS, return
	the corresponding datetime object.  This function goes a little beyond what
	datetime.strptime does in the since that it handle both integer and float
	seconds as well as does the appropriate rounding to get millisecond precision."""
	
	mtch = _dtRE.match(s)
	if mtch is None:
		raise ValueError("Unparsable time string: '%s'" % s)
	else:
		if mtch.group('tz') is None:
			tz = _UTC
		else:
			tzName = mtch.group('tz')
			if tzName in ['UT', 'UTC']:
				tz = _UTC
			elif tzName in ['EST', 'EDT']:
				tz = _EST
			elif tzName in ['CST', 'CDT']:
				tz = _CST
			elif tzName in ['MST', 'MDT']:
				tz = _MST
			elif tzName in ['PST', 'PDT']:
				tz = _PST
			elif tzName in ['LST',]:
				tz = 'LST'
			else:
				raise ValueError("Unknown time zone: '%s'" % tzName)
		
		year = int(mtch.group('year'))
		day = int(mtch.group('day'))
		
		hour = int(mtch.group('hour'))
		minute = int(mtch.group('minute'))
		second = math.floor(float(mtch.group('second')))
		microsecond = int(round((float(mtch.group('second')) - second)*1000)*1000)
		second = int(second)
		
		if mtch.group('mname') is None:
			month = int(mtch.group('month'))
		else:
			monthName = mtch.group('mname').lower()
			if monthName == 'jan':
				month = 1
			elif monthName == 'feb':
				month = 2
			elif monthName == 'mar':
				month = 3
			elif monthName == 'apr':
				month = 4
			elif monthName == 'may':
				month = 5
			elif monthName == 'jun':
				month = 6
			elif monthName == 'jul':
				month = 7
			elif monthName == 'aug':
				month = 8
			elif monthName == 'sep':
				month = 9
			elif monthName == 'oct':
				month = 10
			elif monthName == 'nov':
				month = 11
			elif monthName == 'dec':
				month = 12
			else:
				raise ValueError("Unknown month abbreviation: '%s'" % monthName)
		
		if tz == 'LST':
			# Deal with sidereal times...
			#
			# NOTE:
			# The RMS on this method is ~0.4 seconds over the years 
			# 2000 to 2100.  This should be "good enough" for scheduling
			# purposes.
			
			# Get the position of the observer on the Earth and the Julian 
			# Date of midnight UT for the day we want to map LST to
			obs = site.getObserver()
			dt = astro.date(year, month, day, 0, 0, 0)
			jd = dt.to_jd()
			
			# Get the LST in hours
			LST = hour + minute/60.0 + (second + microsecond/1e6)/3600.0
			
			# Get the Greenwich apparent ST for LST using the longitude of 
			# the site.  The site longitude is stored as radians, so convert
			# to hours first.
			GAST = LST - site.long*12/math.pi
			
			# Get the Greenwich mean ST by removing the equation of the 
			# equinoxes (or some approximation thereof)
			GMST = GAST - _getEquinoxEquation(jd)
			
			# Get the value of D0, days since January 1, 2000 @ 12:00 UT, 
			# and T, the number of centuries since the year 2000.  The value
			# of T isn't terribly important but it is nice to include
			D0 = jd - 2451545.0
			T = D0 / 36525.0
			
			# Solve for the UT hour for this LST and map onto 0 -> 24 hours
			# From: http://aa.usno.navy.mil/faq/docs/GAST.php
			H  = GMST - 6.697374558 - 0.06570982441908*D0 - 0.000026*T**2
			H /= 1.002737909350795
			while H < 0:
				H += 24/1.002737909350795
			while H > 24:
				H -= 24/1.002737909350795
				
			# Get the full Julian Day that this corresponds to
			jd += H/24.0
			
			# Convert the JD back to a time and extract the relevant 
			# quantities needed to build a datetime instance
			dt = astro.get_date(jd)
			
			tz = _UTC
			year = dt.years
			month = dt.months
			day = dt.days
			hour = dt.hours
			minute = dt.minutes
			second = int(dt.seconds)
			microsecond = int((dt.seconds - second)*1e6)
			## Trim the microsecond down to the millisecond level
			microsecond = int(int(microsecond/1000.0)*1000)
			
		# Localize as the appropriate time zone
		dtObject = tz.localize(datetime(year, month, day, hour, minute, second, microsecond))
		
		# Return as UTC
		return dtObject.astimezone(_UTC)


class Observer(object):
	"""Class to hold information about an observer."""
	
	def __init__(self, name, id, first=None, last=None):
		self.name = name
		self.first = first
		self.last = last
		self.id = int(id)

	def joinName(self):
		if self.first != '':
			self.name = ', '.join([self.last, self.first])
		else:
			self.name = self.last
		
	def splitName(self):
		try:
			self.last, self.first = self.name.split(', ', 1)
		except ValueError:
			self.last = self.name
			self.first = ''


class ProjectOffice(object):
	"""Class to hold comments from the LWA object office.  This class isn't really 
	needed to create SD files, but it is helpful for parsing SD files."""
	
	def __init__(self, project=None, sessions=None, observations=None):
		self.project = project
		if sessions is None:
			self.sessions = []
		else:
			self.sessions = sessions
		if observations is None:
			self.observations = []
		else:
			self.observations = observations


class Project(object):
	"""Class to hold all the information about a specific session for a 
	project/proposal."""
	
	def __init__(self, observer, name, id, sessions=None, comments=None, projectOffice=None):
		self.observer = observer
		self.name = name
		self.id = id
		self.comments = comments
		if sessions is None:
			self.sessions = []
		else:
			self.sessions = sessions
		if projectOffice is None:
			self.projectOffice = ProjectOffice()
		else:
			self.projectOffice = projectOffice
		
	def validate(self, verbose=False):
		"""Examine all of the sessions and all of their observations to check
		for validity.  If everything is valid, return True.  Otherwise, return
		False."""
		
		failures = 0
		sessionCount = 1
		for session in self.sessions:
			if verbose:
				print "[%i] Validating session %i" % (os.getpid(), sessionCount)
			if not session.validate(verbose=verbose):
				failures += 1
				
			sessionCount += 1
			
		if failures == 0:
			return True
		else:
			return False
			
	def render(self, session=0, verbose=False):
		"""Create a session definition file that corresponds to the specified 
		session.  Returns the SD file's contents as a string."""
		
		if not self.validate(verbose=verbose) :
			raise RuntimeError("Invalid session/observation parameters.  Aborting.")
		if session >= len(self.sessions):
			raise IndexError("Invalid session index")
		
		self.sessions[session].observations.sort()
		for obs in self.sessions[session].observations:
			obs.dur = obs.getDuration()
		return _SDFTemplate.render(project=self, whichSession=session)


class Session(object):
	"""Class to hold all of the observations in a session."""
	
	def __init__(self, name, id, observations=None, dataReturnMethod='DRSU', comments=None):
		self.name = name
		self.id = int(id)
		if observations is None:
			self.observations = []
		else:
			self.observations = observations
		self.dataReturnMethod = dataReturnMethod
		self.comments = comments
		
		self.cra = 0
		self.drxBeam = -1
		self.spcSetup = [0, 0]
		
		self.recordMIB = {'ASP': -1, 'DP_': -1, 'DR1': -1, 'DR2': -1, 'DR3': -1, 'DR4': -1, 'DR5': -1, 'SHL': -1, 'MCS': -1}
		self.updateMIB = {'ASP': -1, 'DP_': -1, 'DR1': -1, 'DR2': -1, 'DR3': -1, 'DR4': -1, 'DR5': -1, 'SHL': -1, 'MCS': -1}
		
		self.logScheduler = True
		self.logExecutive = True
		
		self.includeStationStatic= False
		self.includeDesign = False

		self.obsFEE = [[-1,-1] for n in xrange(260)]
		self.aspFlt = [-1 for n in xrange(260)]
		self.aspAT1 = [-1 for n in xrange(260)]
		self.aspAT2 = [-1 for n in xrange(260)]
		self.aspATS = [-1 for n in xrange(260)]

		self.tbnGain = -1
		self.drxGain = -1
	
	def setConfigurationAuthority(self, value):
		"""Set the configuration request authority to a particular value in the range of
		0 to 65,535.  Higher values provide higher authority to set FEE and ASP 
		parameters."""
		
		self.cra = int(value)
		
	def setDRXBeam(self, value):
		"""Set the beam to use in the range of 1 to 4 or -1 to let MCS decide."""
		
		self.drxBeam = int(value)
		
	def setSpectrometerChannels(self, value):
		"""Set the number of spectrometer channels to generate, 0 to disable."""
		
		self.spcSetup[0] = int(value)
		
	def setSpectrometerIntegration(self, value):
		"""Set the number of spectrometer FFT integrations to use, 0 to disable."""
		
		self.spcSetup[1] = int(value)
	
	def setMIBRecordInterval(self, component, interval):
		"""Set the record interval for one of the level-1 subsystems (ASP, DP_, etc.) to
		a particular value in minutes.  A KeyError is raised if an invalid sub-system is
		specified.
		
		Special Values are:
		  * -1 = use the MCS default interval
		  * 0 = never record the MIB entries (the entries are still updated, however)
		"""
		
		self.recordMIB[component] = int(interval)
		
	def setMIBUpdateInterval(self, component, interval):
		"""Set the update interval for one of the level-1 subsystems (ASP, DP_, etc.) to 
		a particular value in minutes.  A KeyError is raised if an invalid sub-system is
		specified.
		
		Special Values are:
		  * -1 = use the MCS default interval
		  * 0 = request no updates to the MIB entries
		"""
		
		self.updateMIB[component] = int(interval)
		
	def validate(self, verbose=False):
		"""Examine all of the observations associated with the session to check
		for validity.  If everything is valid, return True.  Otherwise, return
		False."""
		
		failures = 0
		totalData = 0.0
		if self.cra < 0 or self.cra > 65535:
			failures += 1
		if self.drxBeam not in (-1, 1, 2, 3, 4):
			failures += 1
		if self.spcSetup[0] < 0 or self.spcSetup[1] < 0:
			failures += 1
		for key in self.recordMIB.keys():
			if self.recordMIB[key] < -1:
				if verbose:
					print "[%i] Error: Invalid recording interval for '%s' MIB entry '%i'" % (os.getpid(), key, self.recordMIB[key])
				failures += 1
			if self.updateMIB[key] < -1:
				if verbose:
					print "[%i] Error: Invalid update interval for '%s' MIB entry '%i'" % (os.getpid(), key, self.updateMIB[key])
				failures += 1
				
		observationCount = 1
		for obs in self.observations:
			if verbose:
				print "[%i] Validating observation %i" % (os.getpid(), observationCount)
			
			if not obs.validate(verbose=verbose):
				failures += 1
			totalData += obs.dataVolume
			
			observationCount += 1

		# Make sure that the observations don't overlap
		sObs = self.observations
		
		for i in xrange(len(sObs)):
			maxOverlaps = 1
			overlaps = []
			nOverlaps = 0

			for j in xrange(len(sObs)):
				if verbose and i != j:
					print "[%i] Checking for overlap between observations %i and %i" % (os.getpid(), i+1, j+1)

				cStart = int(sObs[j].mjd)*24*3600*1000 + int(sObs[j].mpm)
				cStop = cStart + int(sObs[j].dur)
				pStart = int(sObs[i].mjd)*24*3600*1000 + int(sObs[i].mpm)
				pStop = pStart + int(sObs[i].dur)

				if pStart >= cStart and pStart < cStop:
					nOverlaps += 1
					
					if i != j:
						overlaps.append(j)
			
			if nOverlaps > maxOverlaps:
				if verbose:
					print "[%i] Error: Observation %i overlaps with %s" % (os.getpid(), i+1, ','.join(["%i" % (j+1) for j in overlaps]))
				failures += 1
			
		if totalData >= (2*_DRSUCapacityTB*1024**4):
			if verbose:
				print "[%i] Error: Total data volume for session exceeds %i TB DRSU limit" % (os.getpid(), 2*_DRSUCapacityTB,)
			failures += 1
		
		if failures == 0:
			return True
		else:
			return False
			
	def __cmp__(self, other):
		self.observations.sort()
		other.observations.sort()
		
		startSelf = self.observations[0].mjd + self.observations[0].mpm / (1000.0*3600.0*24.0)
		startOther = other.observations[0].mjd + other.observations[0].mpm / (1000.0*3600.0*24.0)
		if startSelf < startOther:
			return -1
		elif startSelf > startOther:
			return 1
		else:
			return 0


class Observation(object):
	"""Class to hold the specifics of an observations.  It currently
	handles TBW, TBN, TRK_RADEC, TRK_SOL, TRK_JOV, and Stepped"""
	
	id = 1

	def __init__(self, name, target, start, duration, mode, ra, dec, frequency1, frequency2, filter, MaxSNR=False, comments=None):
		self.name = name
		self.target = target
		self.ra = float(ra)
		self.dec = float(dec)
		self.start = start
		self.duration = str(duration)
		self.mode = mode
		self.frequency1 = float(frequency1)
		self.frequency2 = float(frequency2)
		self.filter = int(filter)
		self.MaxSNR = bool(MaxSNR)
		self.comments = comments
		
		self.mjd = None
		self.mpm = None
		self.dur = None
		self.freq1 = None
		self.freq2 = None
		self.beam = None
		self.dataVolume = None
		
		self.update()
		
		# For future use
		self.gain = -1
		
	def __str__(self):
		"""Return a nice string to describe the observation."""
		
		return "%s Obs. of '%s':\n Start %s\n Duration %s\n Filter: %i\n Frequency: %.3f; %.3f\n RA: %.3f\n Dec. %.3f\n" % (self.mode, self.name, self.start, self.duration, self.filter, self.frequency1, self.frequency2, self.ra, self.dec)
		
	def update(self):
		"""Update the computed parameters from the string values."""
		
		self.mjd = self.getMJD()
		self.mpm = self.getMPM()
		self.dur = self.getDuration()
		self.freq1 = self.getFrequency1()
		self.freq2 = self.getFrequency2()
		self.beam = self.getBeamType()
		self.dataVolume = self.estimateBytes()

	def getMJD(self):
		"""Return the modified Julian Date corresponding to the date/time of the
		self.start string."""
		
		utc = parseTimeString(self.start)
		utc = Time(utc, format=Time.FORMAT_PY_DATE)
		return int(utc.utc_mjd)

	def getMPM(self):
		"""Return the number of milliseconds between the date/time specified in the
		self.start string and the previous UT midnight."""
		
		utc = parseTimeString(self.start)
		utcMidnight = datetime(utc.year, utc.month, utc.day, 0, 0, 0, tzinfo=_UTC)
		diff = utc - utcMidnight
		return int(round((diff.seconds + diff.microseconds/1000000.0)*1000.0))

	def getDuration(self):
		"""Parse the self.duration string with the format of HH:MM:SS.SSS to return the
		number of milliseconds in that period."""
		
		fields = self.duration.split(':')
		if len(fields) == 3:
			out = int(fields[0])*3600.0
			out += int(fields[1])*60.0
			out += float(fields[2])
		elif len(fields) == 2:
			out = int(fields[0])*60.0
			out += float(fields[1])
		else:
			out = float(fields[0])
		return int(round(out*1000.0))

	def getFrequency1(self):
		"""Return the number of "tuning words" corresponding to the first frequency."""
		
		freq1 = freq2word(self.frequency1)
		self.frequency1 = word2freq(freq1)
		return freq1

	def getFrequency2(self):
		"""Return the number of "tuning words" corresponding to the second frequency."""
		
		freq2 = freq2word(self.frequency2)
		self.frequency2 = word2freq(freq2)
		return freq2
		
	def getBeamType(self):
		"""Return a valid value for beam type based on whether maximum S/N beam 
		forming has been requested."""
		
		if self.MaxSNR:
			return 'MAX_SNR'
		else:
			return 'SIMPLE'
	
	def estimateBytes(self):
		"""Place holder for functions that return the estimate size of the data
		set being defined by the observation."""
		
		pass
	
	def getFixedBody(self):
		"""Place holder for functions that return ephem.Body objects (or None)
		that define the pointing center of the observation."""
		
		return None
	
	def computeVisibility(self, station=lwa1):
		"""Place holder for functions that return the fractional visibility of the 
		target during the observation period."""
		
		return 1.0
	
	def validate(self, verbose=False):
		"""Place holder for functions that evaluate the observation and return True 
		if it is valid, False otherwise."""
		
		pass
	
	def __cmp__(self, other):
		startSelf = self.mjd + self.mpm / (1000.0*3600.0*24.0)
		startOther = other.mjd + other.mpm / (1000.0*3600.0*24.0)
		if startSelf < startOther:
			return -1
		elif startSelf > startOther:
			return 1
		else:
			return 0


class TBW(Observation):
	"""Sub-class of Observation specifically for TBW observations.  It features a
	reduced number of parameters needed to setup the observation and provides extra
	information about the number of data bits and the number of samples.
	
	.. note::
		TBW read-out times in ms are calculated using (samples/196000+1)*5000 per
		MCS
	
	Required Arguments:
	  * observation name
	  * observation target
	  * observation start date/time (UTC YYYY/MM/DD HH:MM:SS.SSS string)
	  * integer number of samples
	  
	Optional Keywords:
	  * bits - number of data bits (4 or 12)
	  * comments - comments about the observation
	"""
	
	def __init__(self, name, target, start, samples, bits=12, comments=None):
		self.samples = samples
		self.bits = bits
		duration = (int(samples) / _TBW_TIME_SCALE + 1)*_TBW_TIME_GAIN
		durStr = '%02i:%02i:%06.3f' % (int(duration/1000.0)/3600, int(duration/1000.0)%3600/60, duration/1000.0%60)
		Observation.__init__(self, name, target, start, durStr, 'TBW', 0.0, 0.0, 0.0, 0.0, 1, comments=comments)

	def estimateBytes(self):
		"""Estimate the data volume for the specified type and duration of 
		observations.  For TBW:
		
			bytes = samples / samplesPerFrame * 1224 bytes * 260 stands
		"""
		
		SamplesPerFrame = 400
		if self.bits == 4:
			SamplesPerFrame = 1200
		nFrames = self.samples / SamplesPerFrame
		nBytes = nFrames * TBWSize * _nStands
		return nBytes
		
	def validate(self, verbose=False):
		"""Evaluate the observation and return True if it is valid, False
		otherwise."""
		
		failures = 0
		# Basic - Sample size and data bits agreement
		if self.bits not in [4, 12]:
			if verbose:
				print "[%i] Error: Invalid number of data bits '%i'" % (os.getpid(), self.bits)
			failures += 1
		if self.bits == 12 and self.samples > 12000000:
			if verbose:
				print "[%i] Error: Invalid number of samples for 12-bit data (%i > 12000000)" % (os.getpid(), self.samples)
			failures += 1
		if self.bits == 4 and self.samples > 36000000:
			if verbose:
				print "[%i] Error: Invalid number of samples for 4-bit data (%i > 36000000)" % (os.getpid(), self.samples)
			failures += 1
			
		# Advanced - Data Volume
		if self.dataVolume >= (_DRSUCapacityTB*1024**4):
			if verbose:
				print "[%i] Error: Data volume exceeds %i TB DRSU limit" % (os.getpid(), _DRSUCapacityTB)
			failures += 1
			
		# Any failures indicates a bad observation
		if failures == 0:
			return True
		else:
			return False


class TBN(Observation):
	"""Sub-class of Observation specifically for TBN observations.   It features a
	reduced number of parameters needed to setup the observation.
	
	Required Arguments:
	  * observation name
	  * observation target
	  * observation start date/time (UTC YYYY/MM/DD HH:MM:SS.SSS string)
	  * observation duration (HH:MM:SS.SSS string)
	  * observation frequency (Hz)
	  * integer filter code
	  
	Optional Keywords:
	  * comments - comments about the observation
	"""
	
	def __init__(self, name, target, start, duration, frequency, filter, comments=None):
		self.filterCodes = TBNFilters
		Observation.__init__(self, name, target, start, duration, 'TBN', 0.0, 0.0, frequency, 0.0, filter, comments=comments)

	def estimateBytes(self):
		"""Estimate the data volume for the specified type and duration of 
		observations.  For TBN:
		
			bytes = duration * sampleRate / 512 * 1048 bytes * 260 stands * 2 pols.
		"""
		
		try:
			nFrames = self.getDuration()/1000.0 * self.filterCodes[self.filter] / 512
		except KeyError:
			nFrames = 0
		nBytes = nFrames * TBNSize * _nStands * 2
		return nBytes
		
	def validate(self, verbose=False):
		"""Evaluate the observation and return True if it is valid, False
		otherwise.
		
		..note::
			This version of sdf allows for TBN tuning between 5 and 93 MHz.
		"""
		
		failures = 0
		# Basic - Duration, frequency, and filter code values
		if self.dur < 1:
			if verbose:
				print "[%i] Error: Specified a duration of length zero" % os.getpid()
			failures += 1
		if self.freq1 < 109565492 or self.freq1 > 2037918156:
			if verbose:
				print "[%i] Error: Specified frequency is outside of DP tuning range" % os.getpid()
			failures += 1
		if self.filter not in [1,2,3,4,5,6,7]:
			if verbose:
				print "[%i] Error: Invalid filter code '%i'" % (os.getpid(), self.filter)
			failures += 1
			
		# Advanced - Data Volume
		if self.dataVolume >= (_DRSUCapacityTB*1024**4):
			if verbose:
				print "[%i] Error: Data volume exceeds %i TB DRSU limit" % (os.getpid(), _DRSUCapacityTB)
			failures += 1
			
		# Any failures indicates a bad observation
		if failures == 0:
			return True
		else:
			return False

class DRX(Observation):
	"""Sub-class of Observation specifically for DRX observations.
	
	Required Arguments:
	  * observation name
	  * observation target
	  * observation start date/time (UTC YYYY/MM/DD HH:MM:SS.SSS string)
	  * observation duration (HH:MM:SS.SSS string)
	  * observation RA in hours, J2000.0
	  * observation Dec in degrees, J2000.0
	  * observation tuning frequency 1 (Hz)
	  * observation tuning frequency 1 (Hz)
	  * integer filter code
	  
	Optional Keywords:
	  * MaxSNR - specifies if maximum signal-to-noise beam forming is to be used
	    (default = False)
	  * comments - comments about the observation
	"""
	
	def __init__(self, name, target, start, duration, ra, dec, frequency1, frequency2, filter, MaxSNR=False, comments=None):
		self.filterCodes = DRXFilters
		Observation.__init__(self, name, target, start, duration, 'TRK_RADEC', ra, dec, frequency1, frequency2, filter, MaxSNR=MaxSNR, comments=comments)

	def estimateBytes(self):
		"""Estimate the data volume for the specified type and duration of 
		observations.  For DRX:
		
			bytes = duration * sampleRate / 4096 * 4128 bytes * 2 tunings * 2 pols.
		"""
		
		try:
			nFrames = self.getDuration()/1000.0 * self.filterCodes[self.filter] / 4096
		except KeyError:
			nFrames = 0
		nBytes = nFrames * DRXSize * 4
		return nBytes
		
	def getFixedBody(self):
		"""Return an ephem.Body object corresponding to where the observation is 
		pointed.  None if the observation mode is either TBN or TBW."""
		
		pnt = ephem.FixedBody()
		pnt._ra = self.ra / 12.0 * math.pi
		pnt._dec = self.dec / 180 * math.pi
		pnt._epoch = '2000'
		return pnt
		
	def computeVisibility(self, station=lwa1):
		"""Return the fractional visibility of the target during the observation 
		period."""
		
		lwa = station.getObserver()
		pnt = self.getFixedBody()
		
		vis = 0
		cnt = 0
		dt = 0.0
		while dt <= self.dur/1000.0:
			lwa.date = self.mjd + (self.mpm/1000.0 + dt)/3600/24.0 + MJD_OFFSET - DJD_OFFSET
			pnt.compute(lwa)
			
			cnt += 1
			if pnt.alt > 0:
				vis += 1
				
			dt += 300.0
		
		return float(vis)/float(cnt)
		
	def validate(self, verbose=False):
		"""Evaluate the observation and return True if it is valid, False
		otherwise."""
		
		failures = 0
		# Basic - Duration, frequency, and filter code values
		if self.dur < 1:
			if verbose:
				print "[%i] Error: Specified a duration of length zero" % os.getpid()
			failures += 1
		if self.freq1 < 219130984 or self.freq1 > 1928352663:
			if verbose:
				print "[%i] Error: Specified frequency for tuning 1 is outside of DP tuning range" % os.getpid()
			failures += 1
		if self.freq2 < 219130984 or self.freq2 > 1928352663:
			if verbose:
				print "[%i] Error: Specified frequency for tuning 2 is outside of DP tuning range" % os.getpid()
			failures += 1
		if self.filter not in [1,2,3,4,5,6,7]:
			if verbose:
				print "[%i] Error: Invalid filter code '%i'" % (os.getpid(), self.filter)
			failures += 1
			
		# Advanced - Target Visibility
		if self.ra < 0 or self.ra >=24:
			if verbose:
				print "[%i] Error: Invalid value for RA '%.6f'" % (os.getpid(), self.ra)
			failures += 1
		if self.dec < -90 or self.dec > 90:
			if verbose:
				print "[%i] Error: Invalid value for dec. '%+.6f'" % (os.getpid(), self.dec)
			failures += 1
		if self.computeVisibility() < 1.0:
			if verbose:
				print "[%i] Error: Target is only above the horizon for %.1f%% of the observation" % (os.getpid(), self.computeVisibility()*100.0)
			failures += 1
			
		# Advanced - Data Volume
		if self.dataVolume >= (_DRSUCapacityTB*1024**4):
			if verbose:
				print "[%i] Error: Data volume exceeds %i TB DRSU limit" % (os.getpid(), _DRSUCapacityTB)
			failures += 1
			
		# Any failures indicates a bad observation
		if failures == 0:
			return True
		else:
			return False


class Solar(DRX):
	"""Sub-class of DRX specifically for Solar DRX observations.   It features a
	reduced number of parameters needed to setup the observation.
	
	Required Arguments:
	  * observation name
	  * observation target
	  * observation start date/time (UTC YYYY/MM/DD HH:MM:SS.SSS string)
	  * observation duration (HH:MM:SS.SSS string)
	  * observation tuning frequency 1 (Hz)
	  * observation tuning frequency 1 (Hz)
	  * integer filter code
	  
	Optional Keywords:
	  * MaxSNR - specifies if maximum signal-to-noise beam forming is to be used
	    (default = False)
	  * comments - comments about the observation
	"""
	
	def __init__(self, name, target, start, duration, frequency1, frequency2, filter, MaxSNR=False, comments=None):
		self.filterCodes = DRXFilters
		Observation.__init__(self, name, target, start, duration, 'TRK_SOL', 0.0, 0.0, frequency1, frequency2, filter, MaxSNR=MaxSNR, comments=comments)
		
	def getFixedBody(self):
		"""Return an ephem.Body object corresponding to where the observation is 
		pointed.  None if the observation mode is either TBN or TBW."""
		
		return ephem.Sun()


class Jovian(DRX):
	"""Sub-class of DRX specifically for Jovian DRX observations.   It features a
	reduced number of parameters needed to setup the observation.
	
	Required Arguments:
	  * observation name
	  * observation target
	  * observation start date/time (UTC YYYY/MM/DD HH:MM:SS.SSS string)
	  * observation duration (HH:MM:SS.SSS string)
	  * observation tuning frequency 1 (Hz)
	  * observation tuning frequency 1 (Hz)
	  * integer filter code
	  
	Optional Keywords:
	  * MaxSNR - specifies if maximum signal-to-noise beam forming is to be used
	    (default = False)
	  * comments - comments about the observation
	"""
	
	def __init__(self, name, target, start, duration, frequency1, frequency2, filter, MaxSNR=False, comments=None):
		self.filterCodes = DRXFilters
		Observation.__init__(self, name, target, start, duration, 'TRK_JOV', 0.0, 0.0, frequency1, frequency2, filter, MaxSNR=MaxSNR, comments=comments)

	def getFixedBody(self):
		"""Return an ephem.Body object corresponding to where the observation is 
		pointed.  None if the observation mode is either TBN or TBW."""
		
		return ephem.Jupiter()


class Stepped(Observation):
	"""Sub-class of Observation for dealing with STEPPED-mode observations.  It 
	features a reduced number of parameters needed to setup the observation and added
	support for the individual steps.
	
	Required Arguments:
	  * observation name
	  * observation target
	  * observation start date/time (UTC YYYY/MM/DD HH:MM:SS.SSS string)
	  * integer filter code
	  
	Optional Keywords:
	  * steps - array of BeamStep objects that specify the different steps
	  * comments - comments about the observation
	"""
	
	def __init__(self, name, target, start, filter, steps=[], RADec=True, comments=None):
		self.RADec = bool(RADec)
		self.steps = steps
		self.filterCodes = DRXFilters
		Observation.__init__(self, name, target, start, 0, 'STEPPED', 0.0, 0.0, 0.0, 0.0, filter, MaxSNR=False, comments=comments)
		
	def getDuration(self):
		"""Parse the list of BeamStep objects to get the total observation 
		duration as the number of milliseconds in that period."""
		
		duration = 0
		for step in self.steps:
			duration += step.dur
			
		# Update the actual duration string
		self.duration = '%02i:%02i:%06.3f' % (int(duration/1000.0)/3600, int(duration/1000.0)%3600/60, duration/1000.0%60)
		
		return duration
		
	def append(self, newStep):
		"""Add a new BeamStep step to the list of steps."""
		
		self.steps.append(newStep)
		
	def estimateBytes(self):
		"""Estimate the data volume for the specified type and duration of 
		observations.  For DRX:
		
			bytes = duration * sampleRate / 4096 * 4128 bytes * 2 tunings * 2 pols.
		"""
		
		try:
			nFrames = self.getDuration()/1000.0 * self.filterCodes[self.filter] / 4096
		except KeyError:
			nFrames = 0
		nBytes = nFrames * DRXSize * 4
		return nBytes
		
	def computeVisibility(self, station=lwa1):
		"""Return the fractional visibility of the target during the observation 
		period."""
		
		lwa = station.getObserver()
		pnt = self.getFixedBody()
		
		vis = 0
		cnt = 0
		relStart = 0
		for step in self.steps:
			if step.RADec:
				pnt = step.getFixedBody()
				
				dt = 0.0
				while dt <= self.dur/1000.0:
					lwa.date = self.mjd + (relStart/1000.0 + self.mpm/1000.0 + dt)/3600/24.0 + MJD_OFFSET - DJD_OFFSET
					pnt.compute(lwa)
					
					cnt += 1
					if pnt.alt > 0:
						vis += 1
						
					dt += 300.0
			else:
				cnt += 1
				if step.c2 > 0:
					vis += 1
			
			relStart += step.dur
			
		return float(vis)/float(cnt)
		
	def validate(self, verbose=False):
		"""Evaluate the observation and return True if it is valid, False
		otherwise."""
		
		failures = 0
		# Basic - filter setup
		if self.filter not in [1,2,3,4,5,6,7]:
			if verbose:
				print "[%i] Error: Invalid filter code '%i'" % (os.getpid(), self.filter)
			failures += 1
			
		# Basic - steps
		stepCount = 1
		for step in self.steps:
			if verbose:
				print "[%i] Validating step %i" % (os.getpid(), stepCount)
			if not step.validate(verbose=verbose):
				failures += 1
			if step.RADec != self.RADec:
				if verbose:
					print "[%i] Error: Step is not of the same coordinate type as observation" % os.getpid()
				failures += 1
				
			stepCount += 1
			
		# Advanced - Target Visibility
		if self.computeVisibility() < 1.0:
			if verbose:
				print "[%i] Error: Target steps only above the horizon for %.1f%% of the observation" % (os.getpid(), self.computeVisibility()*100.0)
			failures += 1
			
		# Advanced - Data Volume
		if self.dataVolume >= (_DRSUCapacityTB*1024**4):
			if verbose:
				print "[%i] Error: Data volume exceeds %i TB DRSU limit" % (os.getpid(), _DRSUCapacityTB)
			failures += 1
			
		# Any failures indicates a bad observation
		if failures == 0:
			return True
		else:
			return False


class BeamStep(object):
	"""Class for holding all of the information (pointing center, tuning frequencies, 
	etc.)associated with a particular step.  
	
	Required Keywords:
	  * pointing coordinate 1 (RA or azimuth)
	  * pointing coordinate 2 (dec or elevation/altitude)\
	  * observation duration (HH:MM.SS.SSS string)
	  * observation tuning frequency 1 (Hz)
	  * observation tuning frequency 1 (Hz)
	  
	Optional Keywords:
	  * RADec - whether the coordinates are in RA/Dec or Az/El pairs (default=RA/Dec)
	  * MaxSNR - specifies if maximum signal-to-noise beam forming is to be used
	    (default = False)
	  * SpecDelays - 520 list of delays to apply for each antenna
	  * SpecGains - 260 by 2 by 2 list of gains ([[XY, XY], [YX, YY]]) to apply for each antenna
	  
	.. note::
	   If `SpecDelays` is specified, `SpecGains` must also be specified.
	   Specifying both `SpecDelays` and `SpecGains` overrides the `MaxSNR` keyword.
	"""
	
	def __init__(self, c1, c2, duration, frequency1, frequency2, RADec=True, MaxSNR=False, SpecDelays=None, SpecGains=None):
		self.RADec = bool(RADec)
		self.c1 = float(c1)
		self.c2 = float(c2)
		self.duration = duration
		self.frequency1 = float(frequency1)
		self.frequency2 = float(frequency2)
		self.MaxSNR = bool(MaxSNR)
		self.delays = SpecDelays
		self.gains = SpecGains
		
		self.update()
		
	def __str__(self):
		c1s = "RA" if self.RADec else "Az"
		c2s = "Dec" if self.RADec else "Alt"
		return "Step of %s %.3f, %s %.3f for %s at %.3f and %.3f MHz" % (c1s, self.c1, c2s, self.c2, self.duration, self.frequency1/1e6, self.frequency2/1e6)
		
	def update(self):
		"""
		Update the settings.
		"""
		
		self.dur = self.getDuration()
		self.freq1 = self.getFrequency1()
		self.freq2 = self.getFrequency2()
		self.beam = self.getBeamType()
		
	def getDuration(self):
		"""Parse the self.duration string with the format of HH:MM:SS.SSS to return the
		number of milliseconds in that period."""
		
		if type(self.duration).__name__ == 'int':
			return self.duration
		else:
			
			fields = self.duration.split(':')
			if len(fields) == 3:
				out = int(fields[0])*3600.0
				out += int(fields[1])*60.0
				out += float(fields[2])
			elif len(fields) == 2:
				out = int(fields[0])*60.0
				out += float(fields[1])
			else:
				out = float(fields[0])
			return int(round(out*1000.0))
		
	def getFrequency1(self):
		"""Return the number of "tuning words" corresponding to the first frequency."""
		
		freq1 = freq2word(self.frequency1)
		self.frequency1 = word2freq(freq1)
		return freq1

	def getFrequency2(self):
		"""Return the number of "tuning words" corresponding to the second frequency."""
		
		freq2 = freq2word(self.frequency2)
		self.frequency2 = word2freq(freq2)
		return freq2
		
	def getBeamType(self):
		"""Return a valid value for beam type based on whether maximum S/N beam 
		forming has been requested."""
		
		if self.delays is not None and self.gains is not None:
			return 'SPEC_DELAYS_GAINS'
		else:
			if self.MaxSNR:
				return 'MAX_SNR'
			else:
				return 'SIMPLE'
			
	def getFixedBody(self):
		"""Return an ephem.Body object corresponding to where the observation is 
		pointed.  None if the observation mode is either TBN or TBW."""
		
		if self.RADec:
			pnt = ephem.FixedBody()
			pnt._ra = self.c1 / 12.0 * math.pi
			pnt._dec = self.c2 / 180 * math.pi
			pnt._epoch = '2000'
			
		else:
			pnt = None
			
		return pnt
			
	def validate(self, verbose=False):
		"""Evaluate the step and return True if it is valid, False otherwise."""
		
		failures = 0
		# Basic - Delay and gain settings are correctly configured
		if self.delays is not None:
			if len(self.delays) != 520:
				failures += 1
				if verbose:
					print "[%i] Error: Specified delay list had the wrong number of antennas" % os.getpid()
			if self.gains is None:
				failures += 1
				if verbose:
					print "[%i] Error: Delays specified but gains were not" % os.getpid()
		if self.gains is not None:
			if len(self.gains) != 260:
				failures += 1
				if verbose:
					print "[%i] Error: Specified gain list had the wrong number of antennas" % os.getpid()
			if self.delays is None:
				failures += 1
				if verbose:
					print "[%i] Error: Gains specified but delays were not" % os.getpid()
		# Basic - Observation time
		if self.dur < 5:
			if verbose:
				print "[%i] Error: step dwell time (%i ms) is too short" % (os.getpid(), self.dur)
			failures += 1
	     # Basic - Frequency and filter code values
		if self.freq1 < 219130984 or self.freq1 > 1928352663:
			if verbose:
				print "[%i] Error: Specified frequency for tuning 1 is outside of DP tuning range" % os.getpid()
			failures += 1
		if self.freq2 < 219130984 or self.freq2 > 1928352663:
			if verbose:
				print "[%i] Error: Specified frequency for tuning 2 is outside of DP tuning range" % os.getpid()
			failures += 1
		# Advanced - Target Visibility via RA/Dec & Az/El ranging
		if self.RADec:
			if self.c1 < 0 or self.c1 >=24:
				if verbose:
					print "[%i] Error: Invalid value for RA '%.6f'" % (os.getpid(), self.c1)
				failures += 1
			if self.c2 < -90 or self.c2 > 90:
				if verbose:
					print "[%i] Error: Invalid value for dec. '%+.6f'" % (os.getpid(), self.c2)
				failures += 1
		else:
			if self.c1 < 0 or self.c1 > 360:
				if verbose:
					print "[%i] Error: Invalid value for azimuth '%.6f'" % (os.getpid(), self.c1)
				failures += 1
			if self.c2 < 0 or self.c2 > 90:
				if verbose:
					print "[%i] Error: Invalid value for elevation '%.6f'" % (os.getpid(), self.c2)
				failures += 1
		# Any failures indicates a bad observation
		if failures == 0:
			return True
		else:
			return False


def __parseCreateObsObject(obsTemp, beamTemps=[], verbose=False):
	"""Given a obsTemp dictionary of observation parameters and, optionally, a list of
	beamTemp step parameters, return a complete Observation object corresponding to 
	those values."""
	
	# If the observation ID is 0, do nothing.
	if obsTemp['id'] == 0:
		return None
	
	# Create a time string for the start time in UTC.  This is a little tricky 
	# because of the rounding to the nearest millisecond which has to be done
	# to the datetime object.
	start = Time(obsTemp['mjd'] + obsTemp['mpm'] / 1000.0 / 3600.0 / 24.0, format='MJD').utc_py_date
	start += timedelta(microseconds=(int(round(start.microsecond/1000.0)*1000.0)-start.microsecond))
	utcString = start.strftime("UTC %Y %m %d %H:%M:%S.%f")
	utcString = utcString[:-3]
	
	# Build up a string representing the observation duration.  For TBW observations 
	# this needs to be wrapped in a try...expect statement to catch errors.
	try:
		dur = obsTemp['duration']
		dur = float(dur) / 1000.0
		durString = '%02i:%02i:%06.3f' % (dur/3600.0, (dur%3600.0)/60.0, dur%60.0)
	except:
		pass

	# Convert the frequencies from "tuning words" to Hz
	f1 = word2freq(obsTemp['freq1'])
	f2 = word2freq(obsTemp['freq2'])
	
	# Get the mode and run through the various cases
	mode = obsTemp['mode']
	if verbose:
		print "[%i] Obs %i is mode %s" % (os.getpid(), obsTemp['id'], mode)
		
	if mode == 'TBW':
		obsOut = TBW(obsTemp['name'], obsTemp['target'], utcString, 12000000, comments=obsTemp['comments'])
	elif mode == 'TBN':
		obsOut = TBN(obsTemp['name'], obsTemp['target'], utcString, durString, f1, obsTemp['filter'], comments=obsTemp['comments'])
	elif mode == 'TRK_RADEC':
		obsOut = DRX(obsTemp['name'], obsTemp['target'], utcString, durString, obsTemp['ra'], obsTemp['dec'], f1, f2, obsTemp['filter'], MaxSNR=obsTemp['MaxSNR'], comments=obsTemp['comments'])
	elif mode == 'TRK_SOL':
		obsOut = Solar(obsTemp['name'], obsTemp['target'], utcString, durString, f1, f2, obsTemp['filter'], MaxSNR=obsTemp['MaxSNR'], comments=obsTemp['comments'])
	elif mode == 'TRK_JOV':
		obsOut = Jovian(obsTemp['name'], obsTemp['target'], utcString, durString, f1, f2, obsTemp['filter'], MaxSNR=obsTemp['MaxSNR'], comments=obsTemp['comments'])
	else:
		if verbose:
			print "[%i] -> found %i steps" % (os.getpid(), len(beamTemps))
			
		obsOut = Stepped(obsTemp['name'], obsTemp['target'], utcString, obsTemp['filter'], RADec=obsTemp['stpRADec'], steps=[], comments=obsTemp['comments'])
		for beamTemp in beamTemps:
			try:
				dur = beamTemp['duration']
				dur = float(dur) / 1000.0
				durString = '%02i:%02i:%06.3f' % (dur/3600.0, (dur%3600.0)/60.0, dur%60.0)
			except:
				pass
			
			f1 = word2freq(beamTemp['freq1'])
			f2 = word2freq(beamTemp['freq2'])
			obsOut.append( BeamStep(beamTemp['c1'], beamTemp['c2'], durString, f1, f2, obsTemp['stpRADec'], beamTemp['MaxSNR'], beamTemp['delays'], beamTemp['gains']) )

	# Return the newly created Observation object
	return obsOut


def parseSDF(filename, verbose=False):
	"""
	Given a filename, read the file's contents into the SDM instance and return
	that instance.
	"""
	
	# Open the file
	fh = open(filename, 'r')
	
	# Create the keyword regular expression to deal with various indicies included 
	# in the keywords
	kwdRE = re.compile(r'(?P<keyword>[A-Z_0-9\+]+)(\[(?P<id1>[0-9]+?)\])?(\[(?P<id2>[0-9]+?)\])?(\[(?P<id3>[0-9]+?)\])?(\[(?P<id4>[0-9]+?)\])?')
	
	# Create empty objects to get things started.  Values will get filled in as they
	# are found in the file
	po = ProjectOffice()
	observer = Observer('observer_name', 0)
	project = Project(observer, 'project_name', 'project_id', projectOffice=po)
	session = Session('session_name', 0, observations=[])
	project.sessions = [session,]
	project.projectOffice.observations = [[],]
	
	# Loop over the file
	obsTemp = {'id': 0, 'name': '', 'target': '', 'ra': 0.0, 'dec': 0.0, 'start': '', 'duration': '', 'mode': '', 
				'freq1': 0, 'freq2': 0, 'filter': 0, 'MaxSNR': False, 'comments': None, 
				'stpRADec': True, }
	beamTemp = {'id': 0, 'c1': 0.0, 'c2': 0.0, 'duration': 0, 'freq1': 0, 'freq2': 0, 'MaxSNR': False, 'delays': None, 'gains': None}
	beamTemps = []
	sessionBits = 12
	sessionSamples = 12000000
	for line in fh:
		# Trim off the newline character and skip blank lines
		line = line.replace('\n', '')
		if len(line) == 0 or line.isspace():
			continue

		# Split into a keyword, value pair and run it through the regular expression
		# to deal with any indicies present
		try:
			keywordSection, value = line.split(None, 1)
		except:
			continue
		
		mtch = kwdRE.match(keywordSection)
		keyword = mtch.group('keyword')
		
		ids = [-1, -1, -1, -1]
		for i in xrange(4):
			try:
				ids[i] = int(mtch.group('id%i' % (i+1)))
			except TypeError:
				pass
			
		# Skip over the observer comment lines (denoted by a plus sign at the end) 
		# of the keyword
		if keyword[-1] == '+':
			continue
		
		# Observer Info
		if keyword == 'PI_ID':
			project.observer.id = int(value)
			continue
		if keyword == 'PI_NAME':
			project.observer.name = value
			project.observer.splitName()
			continue
		
		# Project/Proposal Info
		if keyword == 'PROJECT_ID':
			project.id = value
			continue
		if keyword == 'PROJECT_TITLE':
			project.name = value
			continue
		if keyword == 'PROJECT_REMPI':
			project.comments = value
			continue
		if keyword == 'PROJECT_REMPO':
			project.projectOffice.project = value
			continue
		
		# Session Info
		if keyword == 'SESSION_ID':
			project.sessions[0].id = int(value)
			continue
		if keyword == 'SESSION_TITLE':
			project.sessions[0].name = value
			continue
		if keyword == 'SESSION_REMPI':
			project.sessions[0].comments = value
			continue
		if keyword == 'SESSION_REMPO':
			project.projectOffice.sessions.append( '' )
			if value[:31] == 'Requested data return method is':
				# Catch for project office comments that are data return related
				project.sessions[0].dataReturnMethod = value[32:]
			else:
				# Catch for standard (not data related) project office comments
				project.projectOffice.sessions[0] = value
			continue
		if keyword == 'SESSION_CRA':
			project.sessions[0].cra = int(value)
			continue
		if keyword[0:12] == 'SESSION_MRP_':
			component = keyword[12:]
			project.sessions[0].recordMIB[component] = int(value)
			continue
		if keyword[0:12] == 'SESSION_MUP_':
			component = keyword[12:]
			project.sessions[0].updateMIB[component] = int(value)
			continue
		if keyword == 'SESSION_LOG_SCH':
			project.sessions[0].logScheduler = bool(value)
			continue
		if keyword == 'SESSION_LOG_EXE':
			project.sessions[0].logExecutive = bool(value)
			continue
		if keyword == 'SESSION_INC_SMIB':
			project.sessions[0].includeStationStatic = bool(value)
			continue
		if keyword == 'SESSION_INC_DES':
			project.sessions[0].includeDesign = bool(value)
			continue
		if keyword == 'SESSION_DRX_BEAM':
			project.sessions[0].drxBeam = int(value)
			continue
		if keyword == 'SESSION_SPC':
			# Remove the ' marks
			value = value.replace("'", "")
			project.sessions[0].spcSetup = [int(i) for i in value.lstrip().rstrip().split(None, 1)]
			# If the input field is '' the value of spcSetup is [].  This
			# isn't good for the SDF render so reset [] to [0, 0]
			if project.sessions[0].spcSetup == []:
				project.sessions[0].spcSetup = [0, 0]
			continue
		
		# Observation Info
		if keyword == 'OBS_ID':
			if obsTemp['id'] != 0:
				project.sessions[0].observations.append( __parseCreateObsObject(obsTemp, beamTemps=beamTemps, verbose=verbose) )
				beamTemp = {'id': 0, 'c1': 0.0, 'c2': 0.0, 'duration': 0, 'freq1': 0, 'freq2': 0, 'MaxSNR': False, 'delays': None, 'gains': None}
				beamTemps = []
			obsTemp['id'] = int(value)
			
			if verbose:
				print "[%i] Started obs %i" % (os.getpid(), int(value))
				
			continue
		if keyword == 'OBS_TITLE':
			obsTemp['name'] = value
			continue
		if keyword == 'OBS_TARGET':
			obsTemp['target'] = value
			continue
		if keyword == 'OBS_REMPI':
			obsTemp['comments'] = value
			continue
		if keyword == 'OBS_REMPO':
			project.projectOffice.observations.append( [] )
			project.projectOffice.observations[0].append( value )
			continue
		if keyword == 'OBS_START_MJD':
			obsTemp['mjd'] = int(value)
			continue
		if keyword == 'OBS_START_MPM':
			obsTemp['mpm'] = int(value)
			continue
		if keyword == 'OBS_DUR':
			obsTemp['duration'] = int(value)
			continue
		if keyword == 'OBS_MODE':
			obsTemp['mode'] = value
			continue
		if keyword == 'OBS_RA':
			obsTemp['ra'] = float(value)
			continue
		if keyword == 'OBS_DEC':
			obsTemp['dec'] = float(value)
			continue
		if keyword == 'OBS_B':
			if value != 'SIMPLE':
				obsTemp['MaxSNR'] = True
			continue
		if keyword == 'OBS_FREQ1':
			obsTemp['freq1'] = int(value)
			continue
		if keyword == 'OBS_FREQ2':
			obsTemp['freq2'] = int(value)
			continue
		if keyword == 'OBS_BW':
			obsTemp['filter'] = int(value)
			continue
		if keyword == 'OBS_STP_RADEC':
			obsTemp['stpRADec'] = bool(int(value))
			continue
			
		# Individual Stepped Beam Observations - This is a bit messy because of
		# trying to keep up when a new step is encountered.  This adds in some 
		# overhead to all of the steps.
		if keyword == 'OBS_STP_C1':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['c1'] = float(value)
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['c1'] = float(value)
			continue
				
		if keyword == 'OBS_STP_C2':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['c2'] = float(value)
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['c2'] = float(value)
			continue
			
		if keyword == 'OBS_STP_T':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['duration'] = int(value)
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['duration'] = int(value)
			continue
				
		if keyword == 'OBS_STP_FREQ1':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['freq1'] = int(value)
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['freq1'] = int(value)
			continue
					
		if keyword == 'OBS_STP_FREQ2':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['freq2'] = int(value)
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['freq2'] = int(value)
			continue
					
		if keyword == 'OBS_STP_B':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				
				if value == 'MAX_SNR':
					beamTemps[-1]['MaxSNR'] = True
					
				elif value == 'SPEC_DELAYS_GAINS':
					beamTemps[-1]['delays'] = []
					beamTemps[-1]['gains'] = []
					for bdi in xrange(2*_nStands):
						beamTemps[-1]['delays'].append( 0 )
						if bdi < _nStands:
							beamTemps[-1]['gains'].append( [0, 0, 0, 0] )
							
				else:
					beamTemps[-1]['MaxSNR'] = False
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
					
				if value == 'MAX_SNR':
					beamTemps[-1]['MaxSNR'] = True
					
				elif value == 'SPEC_DELAYS_GAINS':
					beamTemps[-1]['delays'] = []
					beamTemps[-1]['gains'] = []
					for bdi in xrange(2*_nStands):
						beamTemps[-1]['delays'].append( 0 )
						if bdi < _nStands:
							beamTemps[-1]['gains'].append( [[0, 0], [0, 0]] )
							
				else:
					beamTemps[-1]['MaxSNR'] = False
			continue
			
		if keyword == 'OBS_BEAM_DELAY':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['delays'][ids[1]-1] = int(value)
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['delays'][ids[1]-1] = int(value)
			continue
			
		if keyword == 'OBS_BEAM_GAIN':
			if len(beamTemps) == 0:
				beamTemps.append( copy.deepcopy(beamTemp) )
				beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['gains'][ids[1]-1][ids[2]-1][ids[3]-1] = int(value)
			else:
				if beamTemps[-1]['id'] != ids[0]:
					beamTemps.append( copy.deepcopy(beamTemps[-1]) )
					beamTemps[-1]['id'] = ids[0]
				beamTemps[-1]['gains'][ids[1]-1][ids[2]-1][ids[3]-1] = int(value)
			continue
		
		# Session wide settings at the end of the observations
		if keyword == 'OBS_FEE':
			if ids[0] == 0:
				for n in xrange(len(project.sessions[0].obsFEE)):
					project.sessions[0].obsFEE[n][ids[1]-1] = int(value)
			else:
				project.sessions[0].obsFEE[ids[0]-1][ids[1]-1] = int(value)
			continue
		if keyword == 'OBS_ASP_FLT':
			project.sessions[0].aspFlt[ids[0]-1] = int(value)
			continue
		if keyword == 'OBS_ASP_AT1':
			project.sessions[0].aspAT1[ids[0]-1] = int(value)
			continue
		if keyword == 'OBS_ASP_AT2':
			project.sessions[0].aspAT2[ids[0]-1] = int(value)
			continue
		if keyword == 'OBS_ASP_ATS':
			project.sessions[0].aspATS[ids[0]-1] = int(value)
			continue
		if keyword == 'OBS_TBW_BITS':
			sessionBits = int(value)
			continue
		if keyword == 'OBS_TBW_SAMPLES':
			sessionSamples = int(value)
			continue
		if keyword == 'OBS_TBN_GAIN':
			project.sessions[0].tbnGain = int(value)
			continue
		if keyword == 'OBS_DRX_GAIN':
			project.sessions[0].drxGain = int(value)
			continue
	
	# Create the final observation
	if obsTemp['id'] != 0:
		project.sessions[0].observations.append( __parseCreateObsObject(obsTemp, beamTemps=beamTemps, verbose=verbose) )
		beamTemps = []
		
	# Apply session-wide observation values to the individual observations
	if project.sessions[0].observations[-1].mode == 'TBW':
		for obs in project.sessions[0].observations:
			obs.bits = sessionBits
			obs.samples = int(sessionSamples)
			obs.dur = (obs.samples / _TBW_TIME_SCALE + 1)*_TBW_TIME_GAIN
			obs.duration = '%02i:%02i:%06.3f' % (int(obs.dur/1000.0)/3600, int(obs.dur/1000.0)%3600/60, obs.dur/1000.0%60)

	# Close the file
	fh.close()

	# Return the project
	return project


_SDFTemplate = Template("""
{%- macro renderBW(obs) -%}
	{{ "%.3f MHz"|format(obs.filterCodes[obs.filter]/1000000) if obs.filterCodes[obs.filter] > 1000000 else "%.3f kHz"|format(obs.filterCodes[obs.filter]/1000) }}
{%- endmacro -%}

PI_ID            {{ project.observer.id }}
PI_NAME          {{ project.observer.name }}

{% set poComment = project.projectOffice.project|default('None', boolean=True) -%}
PROJECT_ID       {{ project.id }}
PROJECT_TITLE    {{ project.name }}
PROJECT_REMPI    {{ project.comments|default('None provided', boolean=True)|truncate(4090, killwords=True) }}
PROJECT_REMPO    {{ poComment }}

{% set session = project.sessions[whichSession] -%}
{% set poCommentS = project.projectOffice.sessions[whichSession]|default('None', boolean=True) -%}
{% set poCommentO = project.projectOffice.observations[whichSession]|default('None', boolean=True) -%}
SESSION_ID       {{ session.id }}
SESSION_TITLE    {{ session.name|default('None provided', boolean=True) }}
SESSION_REMPI    {{ session.comments|default('None provided', boolean=True)|truncate(4090, killwords=True) }}
SESSION_REMPO    {{ "Requested data return method is %s"|format(session.dataReturnMethod) if poCommentS == 'None' else poCommentS }}
{{- "\nSESSION_CRA      %i"|format(session.cra) if session.cra != 0 }}
{%- for component in ['ASP', 'DP_', 'DR1', 'DR2', 'DR3', 'DR4', 'DR5', 'SHL', 'MCS'] -%}
{{- "\nSESSION_MRP_%s  %i"|format(component, session.recordMIB[component]) if session.recordMIB[component] != -1 }}
{%- endfor %}
{%- for component in ['ASP', 'DP_', 'DR1', 'DR2', 'DR3', 'DR4', 'DR5', 'SHL', 'MCS'] -%}
{{- "\nSESSION_MUP_%s  %i"|format(component, session.updateMIB[component]) if session.updateMIB[component] != -1 }}
{%- endfor %}
{{- "\nSESSION_LOG_SCH  %i"|format(session.logScheduler) if not session.logScheduler }}
{{- "\nSESSION_LOG_EXE  %i"|format(session.logExecutive) if not session.logExecutive }}
{{- "\nSESSION_INC_SMIB %i"|format(session.includeStationStatic) if session.includeStationStatic }}
{{- "\nSESSION_INC_DES  %i"|format(session.includeDesign) if session.includeDesign }}
{{- "\nSESSION_DRX_BEAM %i"|format(session.drxBeam) if session.drxBeam != -1 }}
{{- "\nSESSION_SPC      %i %i"|format(session.spcSetup[0], session.spcSetup[1]) if session.spcSetup[0] != 0 and session.spcSetup[1] != 0 }}

{% for obs in session.observations -%}
OBS_ID           {{ loop.index }}
OBS_TITLE        {{ obs.name|default('None provided', boolean=True) }}
OBS_TARGET       {{ obs.target|default('None provided', boolean=True) }}
OBS_REMPI        {{ obs.comments|default('None provided', boolean=True)|truncate(4090, killwords=True) }}
OBS_REMPO        {{ "Estimated data volume for this observation is %s"|format(obs.dataVolume|filesizeformat) if poCommentO[loop.index0] == 'None' else poCommentO[loop.index0] }}
OBS_START_MJD    {{ obs.mjd }}
OBS_START_MPM    {{ obs.mpm }}
OBS_START        {{ obs.start }}
OBS_DUR          {{ "%i"|format(obs.dur) }}
OBS_DUR+         {{ "%.1f ms + estimated read-out time"|format(obs.samples / 196000) if obs.mode == 'TBW' else obs.duration }}
OBS_MODE         {{ obs.mode }}
{% if obs.mode == 'TBN' -%}
OBS_FREQ1        {{ obs.freq1 }}
OBS_FREQ1+       {{ "%.9f MHz"|format(obs.frequency1/1000000) }}
OBS_BW           {{ obs.filter }}
OBS_BW+          {{ renderBW(obs) }}
{% elif obs.mode == 'TRK_RADEC' -%}
OBS_RA           {{ obs.ra }}
OBS_DEC          {{ obs.dec }}
OBS_B            {{ obs.beam }}
OBS_FREQ1        {{ obs.freq1 }}
OBS_FREQ1+       {{ "%.9f MHz"|format(obs.frequency1/1000000) }}
OBS_FREQ2        {{ obs.freq2 }}
OBS_FREQ2+       {{ "%.9f MHz"|format(obs.frequency2/1000000) }}
OBS_BW           {{ obs.filter }}
OBS_BW+          {{ renderBW(obs) }}
{% elif obs.mode == 'TRK_SOL' -%}
OBS_B            {{ obs.beam }}
OBS_FREQ1        {{ obs.freq1 }}
OBS_FREQ1+       {{ "%.9f MHz"|format(obs.frequency1/1000000) }}
OBS_FREQ2        {{ obs.freq2 }}
OBS_FREQ2+       {{ "%.9f MHz"|format(obs.frequency2/1000000) }}
OBS_BW           {{ obs.filter }}
OBS_BW+          {{ renderBW(obs) }}
{% elif obs.mode == 'TRK_JOV' -%}
OBS_B            {{ obs.beam }}
OBS_FREQ1        {{ obs.freq1 }}
OBS_FREQ1+       {{ "%.9f MHz"|format(obs.frequency1/1000000) }}
OBS_FREQ2        {{ obs.freq2 }}
OBS_FREQ2+       {{ "%.9f MHz"|format(obs.frequency2/1000000) }}
OBS_BW           {{ obs.filter }}
OBS_BW+          {{ renderBW(obs) }}
{% elif obs.mode == 'STEPPED' -%}
OBS_FREQ1        {{ obs.steps[0].freq1 }}
OBS_FREQ1+       {{ "%.9f MHz"|format(obs.steps[0].frequency1/1000000) }}
OBS_FREQ2        {{ obs.steps[0].freq2 }}
OBS_FREQ2+       {{ "%.9f MHz"|format(obs.steps[0].frequency2/1000000) }}
OBS_BW           {{ obs.filter }}
OBS_BW+          {{ renderBW(obs) }}
OBS_STP_N        {{ obs.steps|length }}
OBS_STP_RADEC    {{ "%i"|format(obs.steps[0].RADec) }}
{% for step in obs.steps -%}
OBS_STP_C1[{{ loop.index }}]      {{ "%f"|format(step.c1) }}
OBS_STP_C2[{{ loop.index }}]      {{ "%+f"|format(step.c2) }}
OBS_STP_T[{{ loop.index }}]       {{ step.dur }}
OBS_STP_FREQ1[{{ loop.index }}]   {{ step.freq1 }}
OBS_STP_FREQ1+[{{ loop.index }}]  {{ "%.9f MHz"|format(step.frequency1/1000000) }}
OBS_STP_FREQ2[{{ loop.index }}]   {{ step.freq2 }}
OBS_STP_FREQ2+[{{ loop.index }}]  {{ "%.9f MHz"|format(step.frequency2/1000000) }}
OBS_STP_B[{{ loop.index }}]       {{ step.beam }}
{% if step.beam == 'SPEC_DELAYS_GAINS' -%}
{% set steploop = loop %}
{% for delay in step.delays -%}
OBS_BEAM_DELAY[{{steploop.index}}][{{loop.index}}] {{step.delays[loop.index0]}}
{% endfor %}
{% for gain in step.gains -%}
OBS_BEAM_GAIN[{{steploop.index}}][{{loop.index}}][1][1] {{step.gains[loop.index0][0][0]}}
OBS_BEAM_GAIN[{{steploop.index}}][{{loop.index}}][1][2] {{step.gains[loop.index0][0][1]}}
OBS_BEAM_GAIN[{{steploop.index}}][{{loop.index}}][2][1] {{step.gains[loop.index0][1][0]}}
OBS_BEAM_GAIN[{{steploop.index}}][{{loop.index}}][2][2] {{step.gains[loop.index0][1][1]}}
{% endfor %}
{%- endif %}
{% endfor %}
{%- endif %}
{% endfor %}

{% for fee in session.obsFEE -%}
{%- if fee[0] != -1 -%}
OBS_FEE[{{ loop.index }}][0]  {{ fee[0] }}
{% endif %}
{%- if fee[1] != -1 -%}
OBS_FEE[{{ loop.index }}][1]  {{ fee[1] }}
{% endif %}
{%- endfor %}
{% for flt in session.aspFlt -%}
{%- if flt != -1 -%}
OBS_ASP_FLT[{{ loop.index }}]  {{ flt }}
{% endif %}
{%- endfor %}
{% for at1 in session.aspAT1 -%}
{%- if at1 != -1 -%}
OBS_ASP_AT1[{{ loop.index }}]  {{ at1 }}
{% endif %}
{%- endfor %}
{% for at2 in session.aspAT2 -%}
{%- if at2 != -1 -%}
OBS_ASP_AT2[{{ loop.index }}]  {{ at2 }}
{% endif %}
{%- endfor %}
{% for ats in session.aspATS -%}
{%- if ats != -1 -%}
OBS_ASP_ATS[{{ loop.index }}]  {{ ats }}
{% endif %}
{%- endfor %}
{%- set obs = session.observations|first -%}
{%- if obs.mode == 'TBW' -%}
OBS_TBW_BITS     {{ obs.bits }}
OBS_TBW_SAMPLES  {{ obs.samples }}
{%- elif obs.mode == 'TBN' -%}
OBS_TBN_GAIN     {{ session.tbnGain }}
{%- else -%}
OBS_DRX_GAIN     {{ session.drxGain }}
{% endif %}

""")

#
# Line removed in the observation loop for dealing the project office comments 
# that was causing problems for jinja2:
#  {% set poComment = project.projectOffice.observations[whichSession][loop.index0]|default('None', boolean=True) -%}
#
