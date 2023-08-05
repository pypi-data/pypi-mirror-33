#!/usr/bin/env python

import numpy
import dedispersion
from matplotlib import pyplot as plt

F0 = 74e6
BW = 1.0e6
DM = 65.891

N = 2**16
P = int(round(N*100.13))
S = 1000*N
S = 2**(int(round(numpy.log10(S)/numpy.log10(2))))

print "=== Pulsar & Data ==="
print "FFT Length: %i (%.3f s)" % (N, float(N)/BW)
print "Pulsar Period: %i (%.3f s)" % (P, float(P)/BW)
print "Dispersion Measure: %.3f pc/cm^3" % DM
print "Data Length: %i (%.3f s; %.1f FFT periods; %.1f pulsar periods)" % (S, float(S)/BW, float(S)/N, float(S)/P)
print " "

print "=== Observations ==="
print "Central Frequency: %.3f MHz" % (F0/1e6,)
print "Bandwidth: %.3f MHz" % (BW/1e6,)
print "Number of Samples Needed for CD: %i" % dedispersion.getCoherentSampleSize(F0, BW, DM)
print " "

data = numpy.zeros(2*S, dtype=numpy.complex64)
data -= data.mean()
for i in xrange(2*P, 2*S, P):
	for j in xrange(-6, 7):
		data[i+j] += 10**(6-abs(j)) * (numpy.random.randn() + 1j*numpy.random.randn())
	
freq  = numpy.fft.fftfreq(2*S, d=1.0/BW) + F0
freq2 = numpy.fft.fftfreq(N, d=1.0/BW) + F0


chirp = dedispersion.__chirpFunction(freq, DM)
data = numpy.fft.fft(data) / chirp
data = numpy.fft.ifft(data)
data = data[S/2:3*S/2]


data += 5*(numpy.random.randn(S) + 1j*numpy.random.randn(S))

#fig = plt.figure()
#ax = fig.gca()
#ax.plot(numpy.linspace(0, 1, S), numpy.fft.ifft(chirp))

wf = numpy.zeros((S/N, N))
for i in xrange(S/N):
	wf[i,:] = numpy.abs( numpy.fft.fft(data[i*N:(i+1)*N]) )**2
	wf[i,:] = numpy.fft.fftshift(wf[i,:])

fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1)
ax1.imshow(10.0*numpy.log10(wf), origin='lower', extent=(freq2[0]/1e6, freq2[-1]/1e6, 0, data.size/N))
ax1.axis('auto')

data2 = dedispersion.coherent(data, F0, BW, DM)
wf2 = numpy.zeros((S/N, N))
for i in xrange(S/N):
	wf2[i,:] = numpy.abs( numpy.fft.fft(data2[i*N:(i+1)*N]) )**2
	wf2[i,:] = numpy.fft.fftshift(wf2[i,:])

ax2 = fig.add_subplot(1, 2, 2)
ax2.imshow(10.0*numpy.log10(wf2), origin='lower', extent=(freq[0]/1e6, freq[-1]/1e6, 0, data2.size/N))
ax2.axis('auto')

plt.show()


