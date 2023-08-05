

def _s(scale, maxScale):
	"""
	Compute an adjustment for the residuals.
	"""
	
	return 1 - 0.6 * scale/maxScale


def _m(x, y, alpha, size=80):
	"""
	Use a Gaussian to scale the beam for Multi-Scale CLEAN.
	"""
	
	r = numpy.sqrt(x**2 + y**2)
	
	scale = 1 - (r/alpha)**2
	Psi = guassian2d = gaussian2d(1.0, size, size, 10, 10)
	
	taper = numpy.zeros((2*size, 2*size))
	for i in xrange(taper.shape[0]):
		for j in xrange(taper.shape[1]):
			taper[i,j] = Psi(i-size, j-size)
			
	taper *= scale
	if alpha == 0:
		taper = numpy.zeros((2*size, 2*size))
		taper[size,size] = 1
	taper /= taper.sum()
	
	return taper


def _computeScaleBeam(beam, scale):
	"""
	Compute the scaled version of the beam.
	"""
	
	x = numpy.zeros_like(beam)
	y = numpy.zeros_like(beam)
	for i in xrange(x.shape[0]):
		x[i,:] = i - beam.shape[0]/2
	for i in xrange(y.shape[1]):
		y[:,i] = i - beam.shape[1]/2
	
	output = convolve(beam, _m(x, y, scale), mode='same')
	
	return output


def _computeScaleBias(beam, scale1, scale2):
	"""
	Compute the scale bias for Multi-Scale CLEAN.
	"""
	
	x = numpy.zeros_like(beam)
	y = numpy.zeros_like(beam)
	for i in xrange(x.shape[0]):
		x[i,:] = i - beam.shape[0]/2
	for i in xrange(y.shape[1]):
		y[:,i] = i - beam.shape[1]/2
	
	output = convolve(beam, _m(x, y, scale1), mode='same')
	output = convolve(output, _m(x, y, scale2), mode='same')
	
	return output


def deconvolveMS(aa, aipyImg, MapSize=80, MapRes=0.50, MapWRes=0.10, lat=34.070, freq=49e6, scales=[0,1,2,4], gain=0.5, maxIter=150, verbose=True):
	"""
	Given a AIPY antenna array instance and an AIPY ImgW instance filled 
	with data, return a deconvolved image.  This function uses a Multi-Scale
	CLEAN-like method that computes the array beam for each peak in the flux.  
	
	Multi-Scale CLEAN tuning parameters:
	  * scales - Pixel scales to clean on (default 0, 1, 2)
	  * gain - CLEAN loop gain (default 0.4)
	  * maxIter - Maximum number of iteration (default 150)
	"""
	
	# Sort scales
	scales.sort()
	
	# Get a grid of hour angle and dec values for the image we are working with
	xyz = aipyImg.get_eq(0.0, lat*numpy.pi/180.0, center=(MapSize,MapSize))
	HA, dec = eq2radec(xyz)
	
	# Get the actual image out of the ImgW instance
	img = aipyImg.image(center=(MapSize,MapSize))
	cleanUp = numpy.where(numpy.isfinite(img), 1, 0)
	
	#mask = numpy.where( numpy.isfinite(img), 0, 1 )
	#img = numpy.ma.array(img, mask=mask)
	#img = img.filled(0)
	
	
	# Setup the arrays to hold the point sources and the residual.
	cleaned = numpy.zeros_like(img)
	working = numpy.zeros_like(img)
	working += img
	
	# Setup the dictionary that will hold the beams as they are computed
	prevBeam = {}
	
	# Go!
	for i in xrange(maxIter):
		# Convolve to the various scales
		peaks = []
		for l in scales:
			peaks.append(_computeScaleBeam(working, l)*cleanUp)
			peaks[-1] *= working.sum() / peaks[-1].sum()
		scaleToUse = -1
		best = -1e22
		for l,m in zip(scales,peaks):
			if m.max() > best:
				best = m.max()
				scaleToUse = l
		print scaleToUse, best
				
		workingS = peaks[scales.index(scaleToUse)]
		
		# Find the location of the peak in the flux density
		peak = numpy.where( workingS == workingS.max() )
		peakX = peak[0][0]
		peakY = peak[1][0]
		peakV = workingS[peakX,peakY]
		
		# Pixel coordinates to hour angle, dec.
		peakHA = HA[peakX, peakY]*180/numpy.pi / 15.0
		peakDec = dec[peakX, peakY]*180/numpy.pi
		
		if verbose:
			currHA  = deg_to_hms(float(peakHA)*15.0)
			currDec = deg_to_dms(float(peakDec))
			
			print "Iteration %i:  Log peak of %.2f at row: %i, column: %i" % (i+1, numpy.log10(peakV), peakX, peakY)
			print "               -> HA: %s, Dec: %s" % (currHA, currDec)
		
		# Check for the exit criteria
		if peakV < 0:
			break
		
		# Find the beam index and see if we need to compute the beam or not
		beamIndex = (peakX,peakY)
		try:
			beam = prevBeam[beamIndex]
		except KeyError:
			if verbose:
				print "               -> Computing beam"
				
			beam = estimateBeam(aa, peakHA, peakDec, 
						MapSize=MapSize, MapRes=MapRes, MapWRes=MapWRes, freq=freq)
			beam /= beam.max()
			prevBeam[beamIndex] = beam
		
		temp = _computeScaleBeam(beam, scaleToUse)
		temp /= temp.max()
		
		comp = numpy.zeros_like(beam)
		comp[peakX,peakY] = 1
		scaledComp = gain*peakV*_computeScaleBeam(comp, scaleToUse)
		scaledBeam = gain*peakV*temp
		
		scaledComp = scaledBeam.sum() / scaledComp.sum()
		
		cleaned += scaledComp
		working -= scaledBeam
		cleaned *= cleanUp
		working *= cleanUp
		
	if verbose:
		# Make an image for comparison purposes if we are verbose
		from matplotlib import pyplot as plt
		
		fig = plt.figure()
		ax1 = fig.add_subplot(2, 2, 1)
		ax2 = fig.add_subplot(2, 2, 2)
		ax3 = fig.add_subplot(2, 2, 3)
		ax4 = fig.add_subplot(2, 2, 4)
		
		c = ax1.imshow(img)
		fig.colorbar(c, ax=ax1)
		ax1.set_title('Input')
		
		d = ax2.imshow(cleaned)
		fig.colorbar(d, ax=ax2)
		ax2.set_title('CLEAN Comps.')
		
		e = ax3.imshow(working)
		fig.colorbar(e, ax=ax3)
		ax3.set_title('Residuals')
		
		#f = ax4.imshow(conv + working)
		#fig.colorbar(f, ax=ax4)
		#ax4.set_title('Final')
		
		plt.show()
	
	# Return
	return conv + working
