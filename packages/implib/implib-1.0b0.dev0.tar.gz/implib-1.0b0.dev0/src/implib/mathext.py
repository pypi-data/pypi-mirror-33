import numpy as np
import struct

# __all__ = ['cmp_vec',
#            'cmp_flt',
#            'np_vec_to_cut_vec',
#            'float_to_cut_string',
#            'np_vec_to_bytes',
#            'compute_checksum']

# mathext --> Math Extended for implant library package.


def get_reserved_bytes(num_bytes):
	return bytes(num_bytes)


def u_int_to_bytes(num, num_bytes):
	if num_bytes == 1:
		return struct.pack('B', num)
	elif num_bytes == 2:
		return struct.pack('H', num)
	elif num_bytes == 4:
		return struct.pack('L', num)
	elif num_bytes == 8:
		return struct.pack('Q', num)
	else:
		return NotImplemented


def str_to_bytes(string, length):
	if string is None or len(string) == 0:
		return bytes(length)
	fmt = '%ss' % length
	return struct.pack(fmt, string.encode('ascii'))


def float_to_bytes(flt):
	return struct.pack('f', flt)


def np_vec_to_bytes(vec):
	return struct.pack('fff', vec[0], vec[1], vec[2])


def compute_checksum(bytes_string):
	return sum(bytes_string)


def np_vec_to_cls_vec(np_vec, decimals=4):
	if np_vec is None or len(np_vec) != 3:
		return ''
	else:
		return '%.*f,%.*f,%.*f' % (decimals, np_vec[0] + 0,
		                           decimals, np_vec[1] + 0,
		                           decimals, np_vec[2] + 0)


def np_vec_to_cut_vec(np_vec, decimals=4):
	"""Converts a 3x1 numpy array to its representation in the CUT domain.
	
	:param np_vec: numpy array or None
	:param decimals: number of decimal places to round each element 
	in np_vec to. - integer - default = 4
	
	:return: Empty string if np_vec is None or len(np_vec) != 3. Otherwise, 
	the string '< x1, x2, x3 >' where x1, x2, x3 are the elements of np_vec
	rounded to decimals decimal places.
	"""
	if np_vec is None or len(np_vec) != 3:
		return ''
	else:
		return '< %.*f, %.*f, %.*f >' % (decimals, np_vec[0] + 0,
		                                 decimals, np_vec[1] + 0,
		                                 decimals, np_vec[2] + 0)


def float_to_cut_string(number, decimals=4):
	"""Converts a float to a rounded string for use in the CUT domain.
	 
	 :param number: float
	 :param decimals: number of decimal places to round each element 
	 in np_vec to. - integer - default = 4
	
	 :return: Empty string if number is None or not a float. Otherwise, round
	 the float to decimals decimal places and convert to a string.
	 """
	if isinstance(number, float) or isinstance(number, int):
		return '%.*f' % (decimals, number)
	else:
		return ''


def cmp_vec(v1, v2, tol):
	"""Evaluates the equality of two vectors within a given tolerance.
	
	:param v1: numpy array or None
	:param v2: numpy array or None
	:param tol: tolerance - float
	
	:return: True if both v1 and v2 are None or is each element in v1 is within 
	tolerance of the corresponding element in v2. False otherwise. 
	"""
	if (v1 is None and v2 is not None) or (v2 is None and v1 is not None):
		return False
	if (v1 is None and v2 is None) or (np.allclose(v1, v2, 0.0, tol)):
		return True
	return False


def cmp_flt(f1, f2, tol):
	"""Evaluates the equality of two floats within a given tolerance.
	
	:param f1: float 
	:param f2: float
	:param tol: tolerance - float
	
	:return: True if f1 and f2 are within tolerance of each other. 
	False otherwise.
	"""
	return abs(float(f1) - float(f2)) < tol
