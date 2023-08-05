import pytest
import numpy as np
from implib.mathext import *


class TestCmpFlt(object):

	def test_expected_input(self):
		# TODO: Test int inputs
		assert cmp_flt(1., 1.0001, 1e-4)
		assert not cmp_flt(1., 1.001, 1e-4)


class TestCmpVec(object):

	def test_none_input(self):
		v1 = [1., 1., 1.]
		tol = 1e-4
		assert cmp_vec(None, None, tol)
		assert not cmp_vec(None, v1, tol)
		assert not cmp_vec(v1, None, tol)

	def test_non_none_input(self):
		v1 = [1., 1., 1.]
		v2 = [1.0001, 1.0001, 1.0001]
		v3 = [1.0001, 1.0001, 1.001]
		tol = 1e-4
		assert cmp_vec(v1, v2, tol)
		assert not cmp_vec(v1, v3, tol)


class TestNumPyVecToCutVec(object):
		v1 = np.array([1.001, 1.0001, 1.00001])
		v1_cut_str = '< 1.001, 1.0001, 1.00001 >'
		v1_cut_str_1dec = '< 1.0, 1.0, 1.0 >'
		v1_cut_str_2dec = '< 1.00, 1.00, 1.00 >'
		v1_cut_str_3dec = '< 1.001, 1.000, 1.000 >'
		v1_cut_str_4dec = '< 1.0010, 1.0001, 1.0000 >'
		v1_cut_str_5dec = '< 1.00100, 1.00010, 1.00001 >'
		v2 = np.array([1.001, -1.23456, 1.23456])
		v2_cut_str = '< 1.0010, -1.2346, 1.2346 >'
		v3 = np.array([-1.00123, 10.00014, 100.00005])
		v3_cut_str = '< -1.0012, 10.0001, 100.0001 >'

		def test_none_input(self):
			assert np_vec_to_cut_vec(None) == ''

		def test_vec_length_not_equal_to_3(self):
			assert np_vec_to_cut_vec(np.array([1])) == ''
			assert np_vec_to_cut_vec(np.array([1,2,3,4])) == ''

		def test_decimals(self):
			assert np_vec_to_cut_vec(self.v1, 1) == self.v1_cut_str_1dec
			assert np_vec_to_cut_vec(self.v1, 2) == self.v1_cut_str_2dec
			assert np_vec_to_cut_vec(self.v1, 3) == self.v1_cut_str_3dec
			assert np_vec_to_cut_vec(self.v1, 4) == self.v1_cut_str_4dec
			assert np_vec_to_cut_vec(self.v1, 5) == self.v1_cut_str_5dec

		def test_rounding(self):
			assert np_vec_to_cut_vec(self.v2) == self.v2_cut_str
			assert np_vec_to_cut_vec(self.v3) == self.v3_cut_str


class TestFloatToCutString(object):
	n1, n2, n3, n4, n5, n6 = 1., 1.0, 1.01, 1.05, -1.0005, -1.0004
	n1_str_1dec = '1.0'
	n1_str_2dec = '1.00'
	n1_str_3dec = '1.000'
	n1_str_4dec = '1.0000'

	def test_non_float_input(self):
		assert float_to_cut_string(None) == ''
		assert float_to_cut_string('not a float') == ''
		assert float_to_cut_string(1234, decimals=4) == '1234.0000'

	def test_decimals(self):
		assert float_to_cut_string(self.n1, decimals=1) == self.n1_str_1dec
		assert float_to_cut_string(self.n1, decimals=2) == self.n1_str_2dec
		assert float_to_cut_string(self.n1, decimals=3) == self.n1_str_3dec
		assert float_to_cut_string(self.n1, decimals=4) == self.n1_str_4dec

	@pytest.mark.xfail
	def test_rounding(self):
		assert float_to_cut_string(self.n1) == '1.0000'
		assert float_to_cut_string(self.n2) == '1.0000'
		assert float_to_cut_string(self.n3) == '1.0100'
		assert float_to_cut_string(self.n3, decimals=1) == '1.0'
		assert float_to_cut_string(self.n4) == '1.0500'
		assert float_to_cut_string(self.n4, decimals=1) == '1.1'
		assert float_to_cut_string(self.n5) == '-1.0005'
		# TODO: for some reason -1.0005 isn't rounding to -1.001 (it's because of the even/odd rounding rule)
		assert float_to_cut_string(self.n5, decimals=3) == '-1.001'
		assert float_to_cut_string(self.n6) == '-1.0004'
		assert float_to_cut_string(self.n6, decimals=3) == '-1.000'
