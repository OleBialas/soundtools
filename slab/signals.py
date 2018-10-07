'''
Base class for Signal data (sounds and filters).
This module uses doctests. Use like so:
python -m doctest slab.py
'''

import copy
import numpy

_default_samplerate = 8000 # Hz

class Signal:
	'''
	Base class for Signal data (sounds and filters)
	Provides duration, nsamples, times, nchannels properties,
	slicing, and conversion between samples and times.
	This class is intended to be subclassed. See Sound class for an example.

	Minimal example:
	class SignalWithInfo(Signal):
	def __init__(self,data,samplerate=None,info=None):
		# call the baseclass init() so that we don't have to repeat that code here:
		super().__init__(data,samplerate)
		# add the new attribute
		self.info = info


	The following arguments are used to initialise a Signal object:

	``data``
		Can be an array, a function or a sequence (list or tuple).
		If its an array, it should have shape ``(nsamples, nchannels)``. If its a
		function, it should be a function f(t). If its a sequence, the items
		in the sequence can be functions, arrays or Signal objects.
		The output will be a multi-channel Signal with channels corresponding to
		Signals for each element of the sequence.
	``samplerate=None``
		The samplerate, if necessary, will use the default (for an array or
		function) or the samplerate of the data (for a filename).

		Examples:
	>>> import slab
	>>> import numpy
	>>> sig = slab.Signal(numpy.ones([10,2]),samplerate=10)
	>>> print(sig)
	<class 'slab.signals.Signal'> duration 1.0, samples 10, channels 2, samplerate 10

		**Properties**
	>>> sig.duration
	1.0
	>>> sig.nsamples
	10
	>>> sig.nchannels
	2
	>>> len(sig.times)
	10

		**Slicing**
	Signal implements __getitem__ and __setitem___ and thus supports slicing.
	Slicing returns numpy.ndarrays or floats, not Signal objects.
	You can also set values using slicing:
	>>> sig[:5] = 0

	will set the first 5 samples to zero.
	You can also select a subset of channels:
	>>> sig[:,1]
	array([0., 0., 0., 0., 0., 1., 1., 1., 1., 1.])

	would be data in the second channel. To extract a channel as a Signal or subclass object
	use sig.channel(1).

	Signals support arithmatic operations (add, sub, mul, truediv, neg ['-sig' inverts phase]):
	>>> sig2 = sig * 2
	>>> sig2[-1,1]
	2.0

		**Static methods**

	Signal.in_samples(time,samplerate)
		Converts time values in seconds to samples.
		This is used to enable input in either samples (int) or seconds (float) in the class.

	Signal.get_samplerate(samplerate)
		Return samplerate if supplied, otherwise return the default samplerate.

	Signal.set_default_samplerate(samplerate)
		Sets the global default samplerate for Signal objects, by default 8000 Hz.

		**Instance methods**

	sig.channel(n)
		Returns the nth channel as new object of the calling class.
		>>> print(sig.channel(0))
		<class 'slab.signals.Signal'> duration 1.0, samples 10, channels 1, samplerate 10

	sig.resize(L)
		Extends or contracts the length of the data in the object in place to have L samples.
		>>> sig.resize(8)
		>>> print(sig)
		<class 'slab.signals.Signal'> duration 0.8, samples 8, channels 2, samplerate 10
	'''

	# instance properties
	nsamples = property(fget=lambda self:self.data.shape[0],
						doc='The number of samples in the Signal.')
	duration = property(fget=lambda self:self.data.shape[0] / self.samplerate,
						doc='The length of the Signal in seconds.')
	times = property(fget=lambda self:numpy.arange(self.data.shape[0], dtype=float) / self.samplerate,
						doc='An array of times (in seconds) corresponding to each sample.')
	nchannels = property(fget=lambda self:self.data.shape[1],
						doc='The number of channels in the Signal.')

	# __methods (class creation, printing, and slice functionality)
	def __init__(self,data,samplerate=None):
		self.samplerate = Signal.get_samplerate(samplerate)
		if isinstance(data, numpy.ndarray):
			self.data = numpy.array(data, dtype='float')
		elif isinstance(data, (list, tuple)):
			kwds = {}
			if samplerate is not None:
				kwds['samplerate'] = samplerate
			channels = tuple(Signal(c, **kwds) for c in data)
			self.data = numpy.hstack(channels)
			self.samplerate = channels[0].samplerate
		else:
			raise TypeError('Cannot initialise Signal with data of class ' + str(data.__class__))
		if len(self.data.shape)==1:
			self.data.shape = (len(self.data), 1)
		elif self.data.shape[1] > self.data.shape[0]:
			self.data = self.data.T

	def __repr__(self):
		return f'{type(self)} (\n{repr(self.data)}\n{repr(self.samplerate)})'

	def __str__(self):
		return f'{type(self)} duration {self.duration}, samples {self.nsamples}, channels {self.nchannels}, samplerate {self.samplerate}'

	def __getitem__(self,key):
		return self.data.__getitem__(key)

	def __setitem__(self,key,value):
		return self.data.__setitem__(key,value)

	# arithmatic operators
	def __add__(self, other):
		new = copy.deepcopy(self)
		if isinstance(other,type(self)):
			new.data = self.data + other.data
		else:
			new.data = self.data + other
		return new
	__radd__ = __add__

	def __sub__(self, other):
		new = copy.deepcopy(self)
		if isinstance(other,type(self)):
			new.data = self.data - other.data
		else:
			new.data = self.data - other
		return new
	__rsub__ = __sub__

	def __mul__(self, other):
		new = copy.deepcopy(self)
		if isinstance(other,type(self)):
			new.data = self.data * other.data
		else:
			new.data = self.data * other
		return new
	__rmul__ = __mul__

	def __truediv__(self, other):
		new = copy.deepcopy(self)
		if isinstance(other,type(self)):
			new.data = self.data / other.data
		else:
			new.data = self.data / other
		return new
	__rtruediv__ = __truediv__

	def __neg__(self):
		new = copy.deepcopy(self)
		new.data = self.data*-1
		return new

	# static methods (belong to the class, but can be called without creating an instance)
	@staticmethod
	def in_samples(ctime,samplerate):
		'''Converts time values in seconds to samples.
		This is used to enable input in either samples (int) or seconds (float) in the class.'''
		if not isinstance(ctime, int):
			ctime = int(numpy.rint(ctime * samplerate))
		return ctime

	@staticmethod
	def get_samplerate(samplerate):
		'Return samplerate if supplied, otherwise return the default samplerate.'
		if samplerate is None:
			return _default_samplerate
		else:
			return samplerate

	@staticmethod
	def set_default_samplerate(samplerate):
		'Sets the global default samplerate for Signal objects, by default 8000 Hz.'
		global _default_samplerate
		_default_samplerate = samplerate

	# instance methods (belong to instances created from the class)
	def channel(self, n):
		'Returns the nth channel as new object of the calling class.'
		new = copy.deepcopy(self)
		new.data = self.data[:, n]
		new.data.shape = (len(new.data), 1)
		return new

	def resize(self, L):
		'Extends or contracts the length of the data in the object in place to have L samples.'
		if isinstance(L,float): # support L in samples or seconds
			L = int(numpy.rint(L*self.samplerate))
		if L == len(self.data):
			pass # already correct size
		elif L < len(self.data):
			self.data = self.data[:L, :]
		else:
			padding = numpy.zeros((L - len(self.data), self.nchannels))
			self.data = numpy.concatenate((self.data, padding))
