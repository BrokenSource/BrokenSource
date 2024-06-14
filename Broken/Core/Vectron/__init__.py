import numpy

numpy.rms = lambda x: numpy.sqrt(numpy.mean(numpy.square(x)))
