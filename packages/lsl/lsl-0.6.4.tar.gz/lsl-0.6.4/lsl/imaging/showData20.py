#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import aipy
import math
import numpy as n

try:
	import sim
	import uvUtils
	import visUtils
	import dp_common
	import lwa_common
	import selfCal
except ImportError, err:
	moduleName = (err.args[0]).split()[-1]
	print "The '%s' module is needed by this file." % moduleName
	sys.exit(-1)

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter


def readUVData(filename, verbose=False, flagTable=None, aa=None, jd=None, phaseCenter='z', maskData=True):
	"""Function to read in a MIRIAD UV file (directory) and return a dictionary
	of the data."""

	uv = aipy.miriad.UV(filename)
	freq = uv['sfreq'] + uv['sdf']*n.arange(uv['nchan'])

	# Apply a channel-based flagging table to the data is requested
	if flagTable is not None:
		toMask = []
		freqMask = []
		for entry in flagTable:
			best = n.where( n.abs(freq-entry) == (n.abs(freq-entry)).min() )
			best = best[0]
			toMask.append( best[0] )
			freqMask.append( freq[best[0]] )

		outString = 'Masking frequencies: '
		for f,c in zip(freqMask, toMask):
			outString = outString + '%.2f MHz (%i) ' % (f/1e6, c)
		print outString

	# Define output data structure
	UVData = {'freq': freq, 'uvw': {}, 'vis': {}, 'wgt': {}, 'msk': {}, 'bls': {}, 'jd': {}}
	if maskData:
		UVData['isMasked'] = True
	else:
		UVData['isMasked'] = False

	uv.select('auto', -1, -1, include=False)
	#uv.select('antennae', 0, -1, include=False)

	# Loop over all data in the UV file
	for (crd,t,(i,j)),d in uv.all():
		if verbose:
			print "Current data for baseline %i-%i, pol. %i -> %s @ %.5f" % (i,j,uv['pol'],aipy.miriad.pol2str[uv['pol']],t)

		# Update the AntennaArray and src information if we have been provided an
		# AntennaArray object
		if aa is not None:
			aa.set_jultime(t)
			if phaseCenter is not 'z':
				phaseCenter.compute(aa)

			# Compute the uvw location of the array for the source and phase to
			# that location in the sky
			try:
				crd = aa.gen_uvw(i, j, src=phaseCenter)
				d = aa.phs2src(d, phaseCenter, i, j)
			except aipy.phs.PointingError:
				continue
		else:
			newCRD = n.zeros((3,uv['nchan']))
			newCRD[0,:] = crd[0]*freq/freq[0]
			newCRD[1,:] = crd[1]*freq/freq[0]
			newCRD[2,:] = crd[2]*freq/freq[0]
			crd = newCRD

			crd.shape = (3,1,freq.shape[0])

		if flagTable is not None:
			d.mask[toMask] = True

		bl = (i,j)
		if maskData:
			bad = n.where( n.abs(d) > 1e6 )[0]
			d.mask[bad] = 1

			uvw = n.squeeze(crd.compress(n.logical_not(d.mask), axis=2))
			vis = d.compressed()
			wgt = n.ones_like(vis) * len(vis)
		else:
			uvw = n.squeeze(crd)
			vis = d
			wgt = n.ones_like(vis) * len(vis.compressed())
		msk = d.mask
		

		if uv['pol'] > -5 or uv['pol'] < -8:
			continue
		else:
			key = aipy.miriad.pol2str[uv['pol']]
			
		if key not in UVData['bls']:
			UVData['bls'][key] = []
			UVData['uvw'][key] = []
			UVData['vis'][key] = []
			UVData['wgt'][key] = []
			UVData['msk'][key] = []
			UVData['jd'][key] = []

		UVData['bls'][key].append( bl  )
		UVData['uvw'][key].append( uvw )
		UVData['vis'][key].append( vis )
		UVData['wgt'][key].append( wgt )
		UVData['msk'][key].append( msk )
		UVData['jd'][key].append( t )
		
	uv.rewind()

	return UVData
	

def makeMap(dataDict, MapSize=30, MapRes=0.5, pol='xx', simDict=None, chanStart=0, chanStop=1, doGain=False):
	"""Given a data dictionary from readUVData, create a set of images.  The images
	are returned as a tuple with elements sky_model, observed, calibrated, beam. 
	If no sky model has been given via the simDict keyword, only the second 
	(observed) and fourth (beam) elements of the tuple are returned."""

	import copy
	origDataDict = copy.copy(dataDict)

	if simDict is not None:
		SelfCal = True
	else:
		SelfCal = False

	im = {}
	if SelfCal:
		# If we are performing a self-calibration, build an image of the model
		im['mdl'] = sim.buildGriddedImage(simDict, MapSize=MapSize, MapRes=MapRes, pol=pol, chan=range(chanStart, chanStop))

		# Build an image to hold the self-calibration results and loop over the different 
		# channels needed to build this map.  The self-calbration is done only for phase
		# and is accomplished using the selfCal function defined in this script.
		im['cal'] = aipy.img.ImgW(size=MapSize, res=MapRes, wres=0.10)
		masterDelay = n.zeros((len(range(chanStart, chanStop)), 20))
		for chan in range(chanStart, chanStop):
			print "Working on channel %i of %i (#%i; %.2f MHz)" % (chan-chanStart+1, chanStop-chanStart, chan, dataDict['freq'][chan]/1e6)
			corrDict, corrDelays = selfCal.selfCal(origDataDict, simDict, MapSize=MapSize, MapRes=MapRes, pol=pol, chan=chan, doGain=doGain, returnDelays=True)

			masterDelay[chan-chanStart,:] = corrDelays

			uvw, vis, wgt = [], [], []
			for u,v,w in zip(corrDict['uvw'][pol], corrDict['vis'][pol], corrDict['wgt'][pol]):
				u = u[:,chan]
				u.shape = (3, 1)
				
				uvw.append(u)
				vis.append(n.array([v[chan]]))
				wgt.append(n.array([w[chan]]))
			uvw = n.concatenate(uvw, axis=1)
			vis = n.concatenate(vis)
			wgt = n.concatenate(wgt)
			
			uvw, vis, wgt = im['cal'].append_hermitian(uvw, vis, wgts=wgt)
			im['cal'].put(uvw, vis, wgts=wgt)

	# Regardless of how we were called, build the observed image
	im[pol] = sim.buildGriddedImage(dataDict, MapSize=MapSize, MapRes=MapRes, pol=pol, chan=range(chanStart,chanStop))

	if SelfCal:
		return (im['mdl'].image(center=(MapSize,MapSize)), 
				im[pol].image(center=(MapSize,MapSize)), 
				im['cal'].image(center=(MapSize,MapSize)), 
				im[pol].bm_image(center=(MapSize,MapSize), term=0), 
				masterDelay)
	else:
		return (im[pol].image(center=(MapSize,MapSize)), 
				im[pol].bm_image(center=(MapSize,MapSize), term=0))


def makeMapSeries(aa, dataDict, MapSize=30, MapRes=0.5, pol='xx', simDict=None, SaveFig=False):
	"""Wrapper around makeMap for building a series of five images spanning the 
	entire frequency range in a data file."""

	fig = plt.figure()

	nChan = len(dataDict['freq'])
	stepSize = int(round(1.0*nChan / 5.0))

	for i in range(5):
		chanStart = i*stepSize
		chanStop = (i+1)*stepSize
		if chanStop > nChan:
			chanStop = nChan-1
		mdl, raw, cal, bm = makeMap(aa, dataDict, MapSize=MapSize, MapRes=MapRes, pol=pol, simDict=simDict, chanStart=chanStart, chanStop=chanStop)

		ax1 = fig.add_subplot(5, 4, 4*i+1)
		ax1.imshow(mdl, extent=(1,-1,-1,1), origin='lower')
		if i == 0:
			ax1.set_title('Sky Model')
		ax1.set_ylabel('%.1f-%.1f MHz' % (dataDict['freq'][chanStart]/1e6, dataDict['freq'][chanStop]/1e6))
		ax1.xaxis.set_major_formatter( NullFormatter() )
		ax1.yaxis.set_major_formatter( NullFormatter() )

		ax2 = fig.add_subplot(5, 4, 4*i+2)
		ax2.imshow(raw, extent=(1,-1,-1,1), origin='lower')
		if i == 0:
			ax2.set_title('Observed')
		ax2.xaxis.set_major_formatter( NullFormatter() )
		ax2.yaxis.set_major_formatter( NullFormatter() )

		ax3 = fig.add_subplot(5, 4, 4*i+3)
		ax3.imshow(cal, extent=(1,-1,-1,1), origin='lower')
		if i == 0:
			ax3.set_title('Calibrated')
		ax3.set_ylabel('%.1f-%.1f MHz' % (dataDict['freq'][chanStart]/1e6, dataDict['freq'][chanStop]/1e6))
		ax3.xaxis.set_major_formatter( NullFormatter() )
		ax3.yaxis.set_major_formatter( NullFormatter() )

		ax4 = fig.add_subplot(5, 4, 4*i+4)
		ax4.imshow(bm, extent=(1,-1,-1,1), origin='lower')
		if i == 0:
			ax4.set_title('Beam')
		ax4.xaxis.set_major_formatter( NullFormatter() )
		ax4.yaxis.set_major_formatter( NullFormatter() )

		for name,src in srcs.iteritems():
			src.compute(aa)
			for ax in [ax1, ax3]:
				top = src.get_crds(crdsys='top', ncrd=3)
				az, alt = aipy.coord.top2azalt(top)
				if alt <= 0:
					continue
				ax.text(top[0], top[1], name, color='white', size=12)
			for ax in [ax1, ax2, ax3, ax4]:
				__plotHorizon(ax)

	plt.show()

	if SaveFig:
		fig.savefig('all-sky-maps.png')


def __plotHorizon(ax, color='white'):
	"""Helper function to plot the horizon line on a sky map."""

	az = n.linspace(0,2*math.pi, 120)
	al = n.zeros_like(az)
	top = n.squeeze(aipy.coord.azalt2top(n.array([[az], [al]])))

	ax.plot(top[0,:], top[1,:], color=color)

def loadData(uvfilename, uvfiledate, TBN=False):
	lwa1 = lwa_common.lwa1()

	dataDict = readUVData(uvfilename, verbose=False)
	junk = {}
	for dt in dataDict['jd']['yy']:
		junk[dt] = 1
	jds = sorted(junk.keys())
	del(junk)
	bls = dataDict['bls']['yy'][0:len(dataDict['bls']['yy'])/len(jds)]
	msk = dataDict['msk']['yy'][0:len(dataDict['bls']['yy'])/len(jds)]

	stands = lwa1.getStands(uvfiledate)

	aa = sim.buildSimArray(lwa1, stands, dataDict['freq'], jd=jds[0])
	
	aa.set_jultime(jds[-1])
	endingZenith = aipy.fit.RadioFixedBody(aa.sidereal_time(), aa.lat, name='zenith at JD%.4f' % jds[-1])
	aa.set_jultime(jds[len(jds)/2])
	middleZenith = aipy.fit.RadioFixedBody(aa.sidereal_time(), aa.lat, name='zenith at JD%.4f' % jds[len(jds)/2])
	aa.set_jultime(jds[0])
	beginningZenith = aipy.fit.RadioFixedBody(aa.sidereal_time(), aa.lat, name='zenith at JD%.4f' % jds[0])

	simDict = sim.buildSimData(aa, sim.srcs, baselines=bls, mask=dataDict['msk']['yy'], jd=jds, phaseCenter=middleZenith)
	del(dataDict)

	# Read in the data for real now with all of the options
	dataDict = readUVData(uvfilename, verbose=False, aa=aa, phaseCenter=middleZenith)

	return (aa, dataDict, simDict)


def calcDelays(dataDict, simDict, stands=None, minCorr=0.90):
	bls = dataDict['bls']['yy']
	delays = n.zeros(190)
	disprs = n.zeros(190)
	for i in range(190):
		delay, dispr = visUtils.fitPhases(dataDict, simDict, baseline=i, minCorr=minCorr, returnDispersion=True, 
									stands=stands, NoPlot=True)
		delays[i] = delay
		disprs[i] = dispr
	
	for refAnt in range(2):
		antDelays = n.zeros(20)
		antWeight = n.zeros(20)
		antWeight[refAnt] = 1.0e9
		for bl in range(190):
			i,j = bls[bl]
			if i == refAnt:
				antDelays[j] = -delays[bl]
				antWeight[j] = 1.0
			else:
				if disprs[bl] == 0:
					continue
				antDelays[j] += (antDelays[i]/antWeight[i]-delays[bl])/disprs[bl]**2
				antWeight[j] += 1/disprs[bl]**2

		out = 'addDelay = {'
		for i in range(20):
			if stands is None:
				print "%3i  %.1f" % (i, (antDelays/antWeight)[i])
			else:
				print "%3i  %.1f" % (stands[i], (antDelays/antWeight)[i])
				out = "%s%i: %.1f, " % (out, stands[i], (antDelays/antWeight)[i])
		print out

def main(args):
	import copy
	import ephem

	# We are using LWA-1
	lwa1 = lwa_common.lwa1()

	uvfilename = 'test-20100916-2230-long.uv'
	uvfiledate = '2010/09/16 22:30:00'

	uvfilename = 'test-20100916-2230-long-hires.uv'
	uvfiledate = '2010/09/16 22:30:00'

	uvfilename = 'test-20100919-2000-long-test.uv'
	uvfiledate = '2010/09/19 20:00:00'

	uvfilename = 'test-tbn-2.uv'
	uvfiledate = '2010/10/07 20:15:00'

	uvfilename = '055498_000000151_1_TBN.uv'
	uvfiledate = '2010/10/26 11:58:00'

	uvfilename = '055507_000003018_1_TBN.uv'
	uvfiledate = '2010/11/07 04:00:00'

	#uvfilename = 'test-20100919-2000-long-hires.uv'
	#uvfiledate = '2010/09/19 20:00:00'

	#uvfilename = 'test-20100919-2000-auto-hihires.uv'
	#uvfiledate = '2010/09/19 20:00:00'

	# Read in the data file just to get the frequencies and Julian Dates in it 
	# and use those to build the simulated array and data sets
	aa, dataDict, simDict = loadData(uvfilename, uvfiledate, TBN=True)
	#calcDelays(dataDict, simDict, stands=n.arange(20))

	#visUtils.plotVisibilities(dataDict, simDict=simDict)
	#visUtils.plotPhases(dataDict, baselines=[15], simDict=simDict, stands=lwa1.getStands(uvfiledate))
	#visUtils.plotClosure(dataDict, antennas=[2,6,16], stands=lwa1.getStands(uvfiledate))
	#visUtils.plotClosure(dataDict, antennas=[11,12,14], stands=lwa1.getStands(uvfiledate))
	visUtils.plotWaterfall(dataDict, simDict=simDict, baseline=1, stands=lwa1.getStands(uvfiledate))
	#visUtils.plotPhaseWaterfall(dataDict, simDict=simDict, baseline=45, stands=lwa1.getStands(uvfiledate))

	#delays1, disprs1 = visUtils.fitPhases(dataDict, simDict, baselines=range(190), width=2,  minCorr=0.95, returnDispersion=True)
	#delays2, disprs2 = visUtils.fitPhases(dataDict, simDict, baselines=[162, 186, 40, 50, 60, 100, 110, 120, 150, 170, 165], width=4,  minCorr=0.95, returnDispersion=True)
	#delays3, disprs3 = visUtils.fitPhases(dataDict, simDict, baselines=range(190), width=8,  minCorr=0.95, returnDispersion=True)
	#delays4, disprs4 = visUtils.fitPhases(dataDict, simDict, baselines=range(190), width=10, minCorr=0.95, returnDispersion=True)

	#masterBL = []
	#for i in range(4):
		#for bl in dataDict['bls']['yy'][0:190]:
			#masterBL.append( bl )
	#masterDelay = n.concatenate([delays1, delays2, delays3, delays4])
	#masterDispr = n.concatenate([disprs1, disprs2, disprs3, disprs4])

	#refAnt = 2
	#antDelay = n.zeros(20)
	#antCount = n.zeros(20)
	#antCount[refAnt] = 1
	#for (i,j),delay, dispr in zip(masterBL, masterDelay, masterDispr):
		#if dispr > 15 or dispr == 0:
			#continue
		#if n.isnan(delay):
			#continue
		
		#if i == refAnt:
			#antDelay[j] += -delay
			#antCount[j] += dispr**-2
		#else:
			#if antDelay[i] == 0:
				#continue
			#else:
				#antDelay[j] += (antDelay[i]-delay)/dispr**2
				#antCount[j] += dispr**-2

	#for a,d in zip(lwa1.getStands(uvfiledate), antDelay/antCount):
		#print a,d
	##for (i,j),delay,dispr in zip(dataDict['bls']['yy'][0:950],delays[1,:],disprs[1,:]):
		##print i,j,delay,dispr
		##if n.isnan(delay) or n.isnan(dispr):
			##continue
		##if dispr < 0.5 or dispr > 10.0:
			##continue
			
		##if i == refAnt:
			##antDelays[j] += -delay/dispr**2
			##antWeight[j] += 1.0/dispr**2
			##antValues[j].append( delay )
		##else:
			##if antDelays[i] == 0:
				##continue
			##antDelays[j] += (antDelays[i] - delay)/dispr**2
			##antWeight[j] += 1.0/dispr**2
			##antValues[j].append( antDelays[i] - delay )
	#for i,delay,values,weights in zip(range(20), (antDelays/antWeight), antValues, antWeights):
		#v = n.array(values)
		#w = n.array(weights)
		#mean = (v*w).sum()/w.sum()
		#std = math.sqrt( (w*(v-mean)**2).sum() / w.sum() )
		#print "%2i  %3i  %.2f  %.2f +/- %.2f" % (i, lwa1.getStands(uvfiledate)[i], delay, mean, std)

	##visUtils.plotPhase(dataDict, baselines=[0])
	#visUtils.plotPhase(simDict, baselines=[0,20])
	#sys.exit()

	#makeMapSeries(aa, dataDict, simDict=simDict, pol='yy', MapSize=80, MapRes=0.50, SaveFig=True)
	#sys.exit()

	#toUse = n.where( (dataDict['freq']>=20.7e6) & (dataDict['freq']<=80.6e6) )
	#chanStart = toUse[0][0]
	#chanStop = toUse[0][-1]
	#raw,bm, = makeMap(aa, dataDict, simDict=simDict, pol='yy', MapSize=80, MapRes=0.50, chanStart=chanStart, chanStop=chanStop, doGain=True)

	#n.savez('delays.npz', dly=dly, freq=dataDict['freq'][toUse][:-1], stands=lwa1.getStands(uvfiledate))

	#fig = plt.figure()
	#for i in range(16):
		#ax1 = fig.add_subplot(4, 4, i+1)
		#ax1.plot(dataDict['freq'][toUse][:-1]/1e6, 2*math.pi*(dly[:,i+1]-0.5))
		#ax1.set_yticks([-math.pi, -math.pi/2, 0, math.pi/2, math.pi])
		#ax1.set_yticklabels(['-$\pi$', '-$\pi$/2', '0', '$\pi$/2', '$\pi$'])
		#ax1.set_title('Stand: %i' % lwa1.getStands(uvfiledate)[i])
		#ax1.set_xlabel('Frequency [MHz]')
		#ax1.set_ylabel('Phase [rad]')
	#plt.show()

	#toUseL = n.where( (dataDict['freq']>=20.7e6) & (dataDict['freq']<=30.6e6) )
	#chanStart = toUseL[0][0]
	#chanStop = toUseL[0][-1]
	#mdlL, rawL, calL, bmL, dlyL = makeMap(aa, dataDict, simDict=simDict, pol='yy', MapSize=80, MapRes=0.50, chanStart=chanStart, chanStop=chanStop, doGain=False)

	toUseH = n.where( (dataDict['freq']>=37.9e6) & (dataDict['freq']<=38.1e6) )
	chanStart = toUseH[0][0]
	chanStop = toUseH[0][-1]
	rawH, bmH = makeMap(dataDict, pol='yy', MapSize=80, MapRes=0.50, chanStart=chanStart, chanStop=chanStop)
	mdlH, bmH = makeMap(simDict, pol='yy', MapSize=80, MapRes=0.50, chanStart=chanStart, chanStop=chanStop)
	#mdlH, rawH, calH, bmH, dlyH = makeMap(dataDict, simDict=simDict, pol='yy', MapSize=80, MapRes=0.50, chanStart=chanStart, chanStop=chanStop, doGain=False)

	fig = plt.figure()

	ax1 = fig.add_subplot(2, 2, 1)
	ax1.imshow(mdlH, extent=(1,-1,-1,1), origin='lower')
	ax1.set_title('Model')
	#ax1.set_ylabel('%.1f-%.1f MHz' % (dataDict['freq'][toUseL[0][0]]/1e6, dataDict['freq'][toUseL[0][-1]]/1e6))
	ax1.xaxis.set_major_formatter( NullFormatter() )
	ax1.yaxis.set_major_formatter( NullFormatter() )

	ax2 = fig.add_subplot(2, 2, 2)
	ax2.imshow(rawH, extent=(1,-1,-1,1), origin='lower')
	ax2.set_title('Raw')
	ax2.xaxis.set_major_formatter( NullFormatter() )
	ax2.yaxis.set_major_formatter( NullFormatter() )

	#ax3 = fig.add_subplot(2, 2, 3)
	#ax3.imshow(calH, extent=(1,-1,-1,1), origin='lower')
	#ax3.set_title('Calibrated')
	##ax3.set_ylabel('%.1f-%.1f MHz' % (dataDict['freq'][toUseH[0][0]]/1e6, dataDict['freq'][toUseH[0][-1]]/1e6))
	#ax3.xaxis.set_major_formatter( NullFormatter() )
	#ax3.yaxis.set_major_formatter( NullFormatter() )

	ax4 = fig.add_subplot(2, 2, 4)
	ax4.imshow(bmH, extent=(1,-1,-1,1), origin='lower')
	ax4.set_title('Beam')
	ax4.xaxis.set_major_formatter( NullFormatter() )
	ax4.yaxis.set_major_formatter( NullFormatter() )

	#for name,src in sim.srcs.iteritems():
		#src.compute(aa)
		#for ax in [ax1, ax3]:
			#top = src.get_crds(crdsys='top', ncrd=3)
			#az, alt = aipy.coord.top2azalt(top)
			#if alt <= 0:
				#continue
			#ax.text(top[0], top[1], name, color='white', size=12)
		#for ax in [ax1, ax2, ax3, ax4]:
			#__plotHorizon(ax)

	plt.show()
	#fig.savefig('2010sep19-2000.png')


if __name__ == "__main__":
	n.seterr(all='ignore')

	main(sys.argv[1:])
