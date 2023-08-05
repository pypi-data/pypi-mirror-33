#!/usr/bin/env python

import sys
import numpy
import scattering
from matplotlib import pyplot as plt

w50 = 0.10000 # s
p   = 0.50000 # s

t = numpy.linspace(-5*p, 5*p, 500)
raw = numpy.exp(-t**2 / (2*(w50/2.35482)))
pbf = scattering.thin(t, 0.40)
obs = numpy.convolve(raw, pbf, 'same')
obs = obs.real
obs *= raw.sum() / obs.sum()
obs += numpy.random.randn(t.size)*0.01

fig = plt.figure()
ax = fig.gca()
ax.plot(t, raw)
ax.plot(t, pbf/2.0/pbf.max())
ax.plot(t, obs)

tScat, merit, cleand = scattering.unscatter(t, obs, 200e-3, 600e-3, 25e-3)
print tScat
ax.plot(t, cleand)

plt.show()
