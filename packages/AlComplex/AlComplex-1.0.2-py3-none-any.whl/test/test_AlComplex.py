import unittest
from AlComplex import * 

a = AlComplex(0,1)
b = AlComplex(1,0)
c = AlComplex(1,1)
d = AlComplex(2,3)
e = AlComplex(1)

class TestFuncs(unittest.TestCase):
	def test_initiation_and_equality(self):
		self.assertEqual(C(0,1), a)
		self.assertEqual(AlComplex(0,1), a)

	def test_AlComplex_addition(self):
		self.assertEqual(a+b, c)
		self.assertEqual(a-b, AlComplex(-1,1))

	def test_AlComplex_multiplication(self):
		self.assertEqual(d*d, AlComplex(-5,12))
		self.assertEqual(C(1,0)*C(0,1), C(0,1))

	def test_AlComplex_potentiation(self):
		self.assertEqual(i**2, -1)
		self.assertEqual((-1)**AlComplex(0,3), exp(-m.pi*3))
		self.assertEqual((-i)**i, exp(m.pi/2))

	def test_AlComplex_division(self):
		self.assertEqual(i/i, 1)
		self.assertEqual(AlComplex(1,0)/i, -i)

	def test_AlComplex_ops_plays_nicely_with_Python_native_types(self):
		self.assertEqual(3*C(9,8), C(27,24))
		
		self.assertEqual(j+4, C(4,1))
		self.assertEqual(j+4.123, C(4.123,1))
		self.assertEqual(j+m.sqrt(4.123), C(m.sqrt(4.123),1))
		self.assertEqual(3 + 1.j + a, C(3, 2))

		self.assertEqual(AlComplex(900)*4, AlComplex(3600))
		self.assertEqual((3-i)/(2+3*i)+(2-2*i)/(1-5*i), 9/13 - 7/13*i)
		
		self.assertEqual(C(4)**1/2, 2)
		
	def test_polar_initialization(self):
		self.assertEqual(AlComplex.polar(1,0), AlComplex(1,0))
		self.assertEqual(AlComplex.polar(1,m.pi/2), i)

	def test_exp(self):
		self.assertEqual(exp(1), m.exp(1))
		self.assertEqual(exp(0), 1)
		self.assertEqual(exp(0+m.pi*i), -1)
		self.assertEqual(exp(m.log(3) - m.pi/2*i), C(0,-3))
		self.assertEqual(4*exp(m.pi/4*i), AlComplex.polar(4, m.pi/4))
		self.assertEqual(exp(m.pi*1.j), -1)

	def test_Ln(self):
		self.assertEqual(Ln(1), 0)
		self.assertEqual(Ln(exp(4+i)), 4+i)
		self.assertEqual(Ln(-1), m.pi*i)
		self.assertEqual(Ln(-i), -m.pi/2*i)

	def test_exponential(self):
		self.assertEqual(i**-1, -i)
		self.assertEqual(C(4)**-1, 1/4)
		self.assertEqual(1.j**-1, -i)

	def test_trigonometric_sin_cos_tan(self):
		self.assertEqual(sin(0), 0)
		self.assertEqual(sin(m.pi/2), 1)
		self.assertEqual(sin(4*i), 1/2*(m.exp(4)-m.exp(-4))*i)
		
		self.assertEqual(cos(0), 1)
		self.assertEqual(cos(m.pi), -1)
		
		self.assertEqual(tan(0), 0)
		self.assertEqual(tan(1+i), sin(1+i)/cos(1+i))
		self.assertEqual(tan(m.pi/4), 1)
		self.assertEqual(tan(1+1.j), sin(1+1.j)/cos(1+1.j))

	def self_hyperbolic_trigonometric_sinh_cosh(self):
		self.assertEqual(-i*sinh(i*a), sin(a))
		self.assertEqual(cos(b), cosh(i*b))
		self.assertEqual(sinh(c), -i*sin(i*c))
		self.assertEqual(cosh(d), cos(d*i))

	def test_int_roots(self):
		l1 = list(int_roots(1, 3))
		l2 = list(int_roots(1.j, 2))
		l5 = list(int_roots(i+2, 10))

		with self.assertRaises(Exception):
			list(int_roots(i, 0))

		self.assertEqual(len(l1), 3)
		self.assertEqual(len(l5), 10)
		self.assertEqual(l1[0]**3, 1)
		self.assertEqual(l2[1]**2, i)
		self.assertEqual(l5[3]**10,i+2)

	def test_ln_n_branch(self):
		self.assertEqual(ln_n_branch(1,0), 0)
		self.assertEqual(ln_n_branch(exp(4+i), 0), 4+i)
		self.assertEqual(ln_n_branch(exp(4+i), 1), 4+i+2*m.pi*i)

	def test_ln_values(self):
		l1 = list(ln_values(i+12, 3, 7))
		l2 = list(ln_values(i, 6, 2))
		l3 = list(ln_values(i, -2, 3))

		self.assertEqual(len(l1), len(l2))
		for k in l1:
			self.assertEqual(exp(k), i+12)

		self.assertIn(-7*m.pi/2*i, l3)
		self.assertIn(-3*m.pi/2*i, l3)
		self.assertIn(m.pi/2*i, l3)
		self.assertIn(5*m.pi/2*i, l3)

	def test_lone_methods_with_Python_number_types(self):
		# Conjugate
		self.assertEqual(conjugate(1), 1)
		self.assertEqual(conjugate(3.j), -3.j)

		# Modulus
		self.assertEqual(modulus(2), 2)
		self.assertEqual(modulus(2.34), 2.34)
		self.assertEqual(modulus(3 + 4.j), 5)

		# Phase
		self.assertEqual(phase(3), 0)
		self.assertEqual(phase(1.j), m.pi/2)