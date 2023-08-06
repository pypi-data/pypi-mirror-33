""" An extended complex number library, with a richer API and compatible with Python numeric types.

It includes functions that are equivalente to the ones found in the cmath module. It alsos includes an
AlComplex object, which wraps a complex number, with a better API.

Every function and mathematical operation available are all compatible with Python own int, float and complex numeric types. 
Also, all the overhead has been supressed as much as possible.
"""

import math as m
import cmath as cm

def use_j(option=True):
	""" Changes the letter used to represent the imaginary unit.

		Parameters
		----------
		option : bool
			Whether to use j over i to represent the imaginary unit in strings.
	"""
	AlComplex.symbol = 'j' if option else 'i'

def real_to_complex(z):
	""" Transforms a basic Python numeric type to AlComplex if it is not one already.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	if not isinstance(z, AlComplex):
		return AlComplex(z.real,z.imag)
	else:
		return z

# Basic Properties

def conjugate(z):
	""" Creates the conjugate of the given number as an AlComplex number.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""

	return AlComplex(z.real, -z.imag)

def modulus(z):
	""" Calculates the given number modulus.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		float
	"""

	return m.sqrt(z.real**2+z.imag**2)

def phase(z):
	""" Calculates the given number main argument.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		float
	"""

	return m.atan2(z.imag,z.real)

def real(z):
	""" Gets the real part of a given number.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		float
	"""

	return z.real

def imaginary(z):
	""" Gets the imaginary part of a given number.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		float
	"""

	return z.imag

# -------- Singly valued Functions --------

def exp(z):
	""" An AlComplex compatible exponential function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""

	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.exp(z.to_python_complex()))

def Ln(z):
	""" An AlComplex compatible natural logarithm function. Gets the main value.

		It uses the main argument of the given number.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex

		See Also
		--------
		ln_n_branch
			Gets a specific branch value, using one of the possible arguments.
		ln_values
			Generates multiple values between given branches.
	"""

	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.log(z.to_python_complex()))

def inverse(z):
	""" Gets the inverse of z.

		It's the number z' such that z/z' = 1. Equivalent to 1/z and z**-1.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""

	z = real_to_complex(z)

	return z**-1

def sqrt(z):
	""" Gets the square root of z.

		Equivalent to z**(1/2)

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""

	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.sqrt(z.to_python_complex()))

# ------- Trigonometric -----------

def sin(z):
	""" An AlComplex compatible sine function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""

	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.sin(z.to_python_complex()))

def cos(z):
	""" An AlComplex compatible cosine function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""

	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.cos(z.to_python_complex()))

def tan(z):
	""" An AlComplex compatible tangent function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.tan(z.to_python_complex()))

def sec(z):
	""" An AlComplex compatible secant function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.sec(z.to_python_complex()))

def csc(z):
	""" An AlComplex compatible cosecant function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.csc(z.to_python_complex()))

def cot(z):
	""" An AlComplex compatible cotangent function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.cot(z.to_python_complex()))

# --------- Hyperbolic Functions -----

def sinh(z):
	""" An AlComplex compatible hyperbolic sine function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.sinh(z.to_python_complex()))

def cosh(z):
	""" An AlComplex compatible hyperbolic cosine function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.cosh(z.to_python_complex()))

def tanh(z):
	""" An AlComplex compatible hyperbolic tangent function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.tanh(z.to_python_complex()))

def sech(z):
	""" An AlComplex compatible hyperbolic secant function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.cosh(z.to_python_complex())**-1)

def csch(z):
	""" An AlComplex compatible hyperbolic cosecant function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.sinh(z.to_python_complex())**-1)

def coth(z):
	""" An AlComplex compatible hyperbolic cotangent function.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.tanh(z.to_python_complex())**-1)

# ----- Inverse Functions -----

def asin(z):
	""" An AlComplex compatible arcsine function. It gets the main value.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.asin(z.to_python_complex()))

def acos(z):	
	""" An AlComplex compatible arccosine function. It gets the main value.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.acos(z.to_python_complex()))

def atan(z):
	""" An AlComplex compatible arctangent function. It gets the main value.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.atan(z.to_python_complex()))

def asinh(z):	
	""" An AlComplex compatible hyperbolic arcsine function. It gets the main value.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.asinh(z.to_python_complex()))

def acosh(z):
	""" An AlComplex compatible hyperbolic arccosine function. It gets the main value.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.acosh(z.to_python_complex()))

def atanh(z):
	""" An AlComplex compatible hyperbolic arctangent function. It gets the main value.

		Parameters
		----------
		z : Python numeric type or AlComplex

		Returns
		-------
		AlComplex
	"""
	z = real_to_complex(z)

	return AlComplex.from_python_complex(cm.atanh(z.to_python_complex()))

# Multiple Valued Functions
def int_roots(z, n, include_self=False):
	""" Generates all the complex n-roots of a number.

	For now, n can only be an integer. Similar to z**(1/n) but this yields all the other branches values.

	Parameters
	----------
	z : Python numeric type or AlComplex
	n : int	
	include_self : bool, optional
		Whether z itself will be yield.

	Yields
	------
	AlComplex
	"""
	if not isinstance(n, int) or n <= 0:
		raise TypeError('The n must be an integer greater than zero.')

	z = real_to_complex(z)

	polar = z.to_polar()
	magnitude = polar[0]**(1/n)
	arg = polar[1]/n

	growth = 2*m.pi/n

	if include_self: yield z

	for k in range(n):
		yield AlComplex.polar(magnitude, arg+k*growth)

def ln_values(z, n_start=0, n_finish=m.inf):
	""" Generates all the possible complex natural logarithm values between certain branches.

	The complex logarithm function is defined as ln(z) = log|z| + i(phase(z)+2pi*n), where n is a natural number. 
	This functions yields all the values by varying n itself.

	Also note that ln_values(z, n1, n2) is a reversed ln_values(z, n2, n1).

	Parameters
	----------
	z : Python numeric type or AlComplex
	n_start : int, optional
		The beginning n in the formula above.
	n_finish : int or bool, optional
		The last n in the formula above. If smaller than n_start, the n will be decreacing in the sequence 
		given by the formula above

	Yields
	------
	AlComplex
	"""
	if (not isinstance(n_start, int) or 
			(n_finish is not False and not isinstance(n_start, int))):
			raise TypeError('The starting and finishing numbers must be integers.')

	z = real_to_complex(z)

	real = m.log(z.abs())
	arg = z.phase()

	counter = n_start
	step = 1 if (n_start <= n_finish) else -1

	while counter != n_finish:
		yield AlComplex(real, arg + 2*m.pi*counter)	
		counter += step

def ln_n_branch(z,n):
	""" Gets the specific value of the complex logarithm in a certain branch.

	The complex logarithm function is defined as ln(z) = log|z| + i(phase(z)+2pi*n), where n is an integer. 
	This functions returns the specific value of the function for the given n.

	Parameters
	----------
	z : Python numeric value or AlComplex
	n : int
	Yields
	------
	AlComplex
	"""
	if not isinstance(n, int):
		raise TypeError('The n must be an integer.')

	return Ln(z) + 2*m.pi*n*i	

class AlComplex():
	""" Creates a complex number with rectangular coordinates.

	Atributes
	---------

	symbol : str
		How the imaginary unit will be represented (i or j).
	precission : float
		The error margin of complex numbers components. Used for calculating equalities.
	real : float
		The real part of the complex number.
	imag : float
		The imaginary part of the complex number.

	Parameters
	----------
	r : int or float
		The real part of the complex number.
	i : int or float, optional
		The imaginary part of the complex number
	"""
	def __init__(self, r, i=0):
		# Since sin(pi) != 0 thanks to float precission, but a number very very small, we put this guard.
		if abs(r) < AlComplex.precission: r = 0
		if abs(i) < AlComplex.precission: i = 0

		if isinstance(r, AlComplex): r = r.to_float
		if isinstance(i, AlComplex): i = i.to_float

		self.imag = float(i)
		self.real = float(r)

	symbol = 'i'
	precission = 1e-14

	def polar(r, arg):
		""" Creates an AlComplex number from the given polar coordinates.

		Parameters
		----------
		r : int or float
			The modulo of the desired complex number.
		arg : int or float
			The argument in radians of the desided complex number.

		Returns
		-------
		AlComplex
		"""

		return AlComplex(round(r*m.cos(arg), 15), round(r*m.sin(arg),15))

	def from_python_complex(n):
		""" Wraps a Python standard complex number in an AlComplex number.

		Parameters
		----------
		n : complex

		Returns
		-------
		AlComplex
		"""

		return AlComplex(n.real, n.imag)
	
	def to_polar(self):
		""" Gives the polar representation of the AlComplex number.

		Returns
		-------
		(float, float)
			A tuple of the form (modulus, main argument).
		"""

		return (self.abs(), self.phase())

	def to_rect_coord(self):
		""" Gives the rectangular coordinates representation of the AlComplex number.

		Returns
		-------
		(float, float)
			A tuple of the form (real part, imaginary part).
		"""

		return (self.real, self.imag)

	def to_python_complex(self):
		""" Forms a standard Python complex number from the AlComplex number components.

		Returns
		-------
		complex
		"""

		return self.real + self.imag*1.j

	def to_float(self):
		""" Converts an AlComplex number to a float if it only has a real part.

		Returns
		-------
		float

		Raises
		------
		TypeError
			If the imaginary part of the AlComplex number is not zero.
		"""

		if self.imag == 0:
			return float(self.real)
		else:
			raise TypeError('Cannot convert to float; imaginary part is not zero.')

	def to_int(self):
		""" Converts an AlComplex number to an int if it only has a real part.

		Returns
		-------
		int

		Raises
		------
		TypeError
			If the imaginary part of the AlComplex number is not zero.
		"""

		if self.imag == 0:
			return int(self.real)
		else:
			raise TypeError('Cannot convert to int; imaginary part is not zero.')

	def abs(self):
		""" Calculates the modulus of self.

		Returns
		-------
		float

		See Also
		--------
		modulus, magnitude
		"""

		return modulus(self)

	def modulus(self):
		""" Calculates the modulus of self.

		Returns
		-------
		float

		See Also
		--------
		abs, magnitude
		"""

		return modulus(self)

	def magnitude(self):
		""" Calculates the modulus of self.

		Returns
		-------
		float

		See Also
		--------
		modulus, abs
		"""

		return modulus(self)

	def phase(self):
		""" Finds the principal argument in radians of self.

		Returns
		-------
		float

		See Also
		--------
		arg, angle
		"""

		return phase(self)

	def arg(self):
		""" Finds the principal argument in radians of self.

		Returns
		-------
		float

		See Also
		--------
		arg, angle
		"""

		return phase(self)

	def angle(self):
		""" Finds the principal argument in radians of self.

		Returns
		-------
		float

		See Also
		--------
		arg, phase
		"""

		return phase(self)

	def conjugate(self):
		""" Gives the conjugate of self as an AlComplex number.

		Returns
		-------
		AlComplex
		"""

		return conjugate(self)

	# Operator Overloading
	def __abs__(self):
		return modulus(self)

	def __neg__(self):
		return AlComplex(-self.real, -self.imag)

	def __add__(self, z):
		z = real_to_complex(z)

		return AlComplex(self.real + z.real, self.imag + z.imag)

	def __radd__(self, z):
		return self + z

	def __mul__(self,z):
		z = real_to_complex(z)

		return AlComplex(self.real*z.real - self.imag*z.imag, 
			self.real*z.imag + self.imag*z.real)

	def __rmul__(self,z):
		return self*z

	def __sub__(self, z):
		z = real_to_complex(z)
		
		return AlComplex(self.real - z.real, self.imag - z.imag)

	def __rsub__(self,z):
		return -self + z

	def __truediv__(self, z):
		z = real_to_complex(z)

		return self*z**-1

	def __rtruediv__(self, z):
		return self**-1*z

	def __pow__(self, z):
		z = real_to_complex(z)

		return exp(z*Ln(self))

	def __rpow__(self, z):
		z = real_to_complex(z)

		return exp(self*Ln(z))

	def __eq__(self,z):
		z = real_to_complex(z)

		# We use this to avoid the typical imprecissions the floating point calculations
		return (m.isclose(z.real,self.real, abs_tol=self.precission) 
			and m.isclose(z.imag ,self.imag, abs_tol=self.precission))	

	def __repr__(self):
		return str(self)

	def __str__(self):
		sign = ' - ' if self.imag < 0 else ' + '
		return str(self.real) + sign + str(abs(self.imag)) + AlComplex.symbol		

""" A shorter alias for constructing complex numbers.
"""
C = AlComplex

""" The complex unit. 
"""
j = i = I = J = AlComplex(0,1)