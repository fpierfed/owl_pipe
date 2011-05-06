#!/usr/bin/env python
import numpy
import pyfits




name = 'test.fits'
data = numpy.random.random((512, 512))
hdu = pyfits.PrimaryHDU(data)
hdu.writeto(name)
