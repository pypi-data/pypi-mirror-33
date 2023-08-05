import re
import struct
import numpy as np
from .cutcmds import *
from .fileutils import *
from .mathext import *

__all__ = ['read_cls_cut_file',
           'read_binary_cut_file',
           'read_ascii_cut_file',
           'read_cut_file',
           'is_cmd_list',
           'make_cbf_header',
           'make_goto_cmd']

# TODO: Add documentation

float_re = r'(-?\d+\.?\d*)'
comma_re = r' *, *'
vec_re = r'< *' + float_re + comma_re + float_re + comma_re + float_re + r' *>'

ASCII_ARG_TYPE = {
	'VEC': {'re': re.compile(vec_re, re.ASCII), 'conv_func': (lambda mo: np.array(mo.groups(), dtype=float))},
	'FLOAT': {'re': re.compile(float_re, re.ASCII), 'conv_func': (lambda mo: float(mo.group()))},
	'STR': {'re': re.compile(r'(\w+)', re.ASCII), 'conv_func': (lambda mo: mo.group())},
	'BYTE': {'re': re.compile(r'(\d{1,3})', re.ASCII), 'conv_func': (lambda mo: int(mo.group()))},
	'LNGINT': {'re': re.compile(r'(\d{1,10})', re.ASCII), 'conv_func': (lambda mo: mo.group())},
	# Should refine the character set
	'LNGSTR': {'re': re.compile(r'(.*)\n', re.ASCII), 'conv_func': (lambda mo: mo.group(1))},
}

ASCII_CMD_TO_CUT_CMD = {
		'header': {'cmd': HeaderCmd, 'args': ['LNGSTR']},
		'header_ext': {'cmd': HeaderExtCmd, 'args': ['LNGSTR']},
		'checkpoint': {'cmd': CheckpointCmd, 'args': ['STR', 'VEC', 'FLOAT']},
		'cutter': {'cmd': CutterCmd, 'args': ['STR', 'FLOAT', 'FLOAT', 'FLOAT']},
		'orient': {'cmd': OrientCmd, 'args': ['VEC']},
		'orient5b': {'cmd': Orient5XCmd, 'args': ['VEC', 'VEC']},
		'phase': {'cmd': PhaseCmd, 'args': ['STR']},
		'startshape': {'cmd': StartshapeCmd, 'args': ['STR', 'BYTE']},
		'endshape': {'cmd': EndshapeCmd, 'args': ['STR', 'BYTE']},
		'decel_off': {'cmd': DecelOffCmd, 'args': None},
		'decel_on': {'cmd': DecelOnCmd, 'args': None},
		'point': {'cmd': PointCmd, 'args': ['VEC']},
		'line': {'cmd': LineCmd, 'args': ['VEC', 'VEC']},
		'line5b': {'cmd': Line5XCmd, 'args': ['VEC', 'VEC', 'VEC', 'VEC']},
		'speed': {'cmd': SpeedCmd, 'args': ['FLOAT']},
		'accel': {'cmd': AccelCmd, 'args': ['FLOAT', 'FLOAT']},
		'cutter_on': {'cmd': CutterOnCmd, 'args': None},
		'cutter_off': {'cmd': CutterOffCmd, 'args': None},
		'fcparms': {'cmd': FCparmsCmd, 'args': ['FLOAT', 'FLOAT', 'FLOAT', 'FLOAT']},
		'version': {'cmd': VersionCmd, 'args': ['STR', 'STR']},
		'comment': {'cmd': CommentCmd, 'args': ['LNGSTR']},
		'check_sum': {'cmd': CheckSumCmd, 'args': ['LNGINT']}
}


def parse_ascii_cut_line(line):
	split_result = line.split()
	ascii_cmd = split_result[0]
	ascii_args = None if len(split_result) == 1 else line.split(' ', 1)[1]

	if ascii_cmd not in ASCII_CMD_TO_CUT_CMD.keys():
		raise InvalidCutCmdError(ascii_cmd)
	elif ASCII_CMD_TO_CUT_CMD[ascii_cmd]['args'] is None:
		return ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd']()
	elif ascii_args is None:
		# TODO: Remove [None]
		return ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd']([None])
	else:
		arg_list = []
		for arg_type in ASCII_CMD_TO_CUT_CMD[ascii_cmd]['args']:
			mo = ASCII_ARG_TYPE[arg_type]['re'].search(ascii_args)
			arg_list.append(ASCII_ARG_TYPE[arg_type]['conv_func'](mo))
			ascii_args = ascii_args[mo.span(0)[1]:]
		return ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd'](arg_list)
	raise RuntimeError('Error parsing ASCII CUT line.')


# TODO: Add try-catch
def read_ascii_cut_file(file_path):
	"""Convert an ASCII cut file to a list of CutCmds."""
	with open(file_path, 'r') as f:
		cmd_list = []
		num_lines = 0
		for line in f:
			num_lines += 1
			cmd_list.append(parse_ascii_cut_line(line))
			# split_result = line.split()
			# ascii_cmd = split_result[0]
			# ascii_args = None if len(split_result) == 1 else line.split(' ', 1)[1]
			#
			# if ascii_cmd not in ASCII_CMD_TO_CUT_CMD.keys():
			# 	raise InvalidCutCmdError(ascii_cmd)
			# elif ASCII_CMD_TO_CUT_CMD[ascii_cmd]['args'] is None:
			# 	cmd_list.append(ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd']())
			# elif ascii_args is None:
			# 	# TODO: Remove [None]
			# 	cmd_list.append(ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd']([None]))
			# else:
			# 	arg_list = []
			# 	for arg_type in ASCII_CMD_TO_CUT_CMD[ascii_cmd]['args']:
			# 		mo = ASCII_ARG_TYPE[arg_type]['re'].search(ascii_args)
			# 		arg_list.append(ASCII_ARG_TYPE[arg_type]['conv_func'](mo))
			# 		ascii_args = ascii_args[mo.span(0)[1]:]
			# 	cmd_list.append(ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd'](arg_list))

		assert num_lines == len(cmd_list), 'ERROR: %s lines in CUT but only %s commands!' % (
			num_lines, len(cmd_list))
		return cmd_list

# TODO: add int and unpack using struct
BIN_ARG_TYPE = {
	's': (lambda hex_int_lst: ''.join([chr(c) for c in hex_int_lst]).rstrip('\x00')),
	'f': (lambda x: struct.unpack('<f', x)[0]),
	'b': (lambda x: x),
	'v': (lambda x: [struct.unpack('<f', x[:4])[0], struct.unpack('<f', x[4:8])[0], struct.unpack('<f', x[8:])[0]]),
	'i': (lambda x: struct.unpack('<B', x)[0]),  # single Byte integer
	'x': (lambda x: list(x)),  # hex
	'h': (lambda x: struct.unpack('<H', x)[0]),  # short
	'r': (lambda x: x)  # reserved byte. TODO: Should this return empty list?
}

BIN_CMD_TO_CUT_CMD = {
	0x53A1B792: {'cmd': HeaderCmd, 'bin_args': [('x', 4), ('x', 4), ('x', 2), ('x', 6), ('h', 2), ('s', 70), ('s', 34),
	                                            ('h', 2), ('x', 4)]},
	0x3C: {'cmd': CheckpointCmd, 'bin_args': [('s', 16), ('v', 12), ('f', 4)]},
	0xA3: {'cmd': CutterCmd, 'bin_args': [('s', 16), ('f', 4), ('f', 4), ('f', 4), ('r', 4)]},
	0x58: {'cmd': OrientCmd, 'bin_args': [('v', 12), ('r', 4), ('r', 4), ('r', 4)]},
	0x59: {'cmd': Orient5XCmd, 'bin_args': [('v', 12), ('v', 12)]},
	0x21: {'cmd': PhaseCmd, 'bin_args': [('s', 16)]},
	0xC9: {'cmd': StartshapeCmd, 'bin_args': [('s', 5), ('i', 1)]},
	0x65: {'cmd': EndshapeCmd, 'bin_args': [('s', 5), ('i', 1)]},
	0x2B: {'cmd': DecelOffCmd, 'bin_args': [('r', 0)]},
	0x4E: {'cmd': DecelOnCmd, 'bin_args': [('r', 0)]},
	0x33: {'cmd': PointCmd, 'bin_args': [('v', 12)]},
	0xB6: {'cmd': LineCmd, 'bin_args': [('v', 12), ('v', 12)]},
	0xB7: {'cmd': Line5XCmd, 'bin_args': [('v', 12), ('v', 12), ('v', 12), ('v', 12)]},
	0x8B: {'cmd': SpeedCmd, 'bin_args': [('f', 4)]},
	0x47: {'cmd': AccelCmd, 'bin_args': [('f', 4), ('f', 4)]},
	0xBB: {'cmd': CutterOnCmd, 'bin_args': [('r', 0)]},
	0x66: {'cmd': CutterOffCmd, 'bin_args': [('r', 0)]},
	0xFC: {'cmd': FCparmsCmd, 'bin_args': [('f', 4), ('f', 4), ('f', 4), ('f', 4)]},
	0x55: {'cmd': VersionCmd, 'bin_args': [('s', 8), ('s', 8)]},
	0x5A: {'cmd': CommentCmd, 'bin_args': [('s', 40)]},
	'bin_cmd_hdr': {'bin_args': [('i', 1), ('i', 1), ('i', 1), ('r', 1), ('x', 2)]}
}


# TODO: Where to add cbf format checker? Add it to the parser?
def read_binary_cut_file(file_path):
	"""Convert a binary cut file to a list of CutCmds."""

	with open(file_path, 'rb') as f:
		def bin_chunks_to_py(bin_chunks):
			lst = []
			for typ, sz in bin_chunks:
				lst.append(BIN_ARG_TYPE[typ](f.read(sz)))
			return lst

		cmd_lst = []
		header = bin_chunks_to_py(BIN_CMD_TO_CUT_CMD[0x53A1B792]['bin_args'])
		# TODO: process header and add it to command list
		cmd_lst.append(BIN_CMD_TO_CUT_CMD[0x53A1B792]['cmd']([header[5]]))
		while True:
			cmd_code = f.read(2)
			if not cmd_code:
				# eof
				break
			chunk = bin_chunks_to_py(BIN_CMD_TO_CUT_CMD['bin_cmd_hdr']['bin_args'])
			bin_cmd = chunk[1]
			if bin_cmd not in BIN_CMD_TO_CUT_CMD.keys():
				raise InvalidCutCmdError(bin_cmd)
			else:
				arg_list = bin_chunks_to_py(BIN_CMD_TO_CUT_CMD[bin_cmd]['bin_args'])
				if arg_list == ['']:
					arg_list = [None]
				cmd_lst.append(BIN_CMD_TO_CUT_CMD[bin_cmd]['cmd'](arg_list))
		return cmd_lst


CLS_CMD_TO_CUT_CMD = {
	'$$ ': {'cmd': None},
	'$$CUT': {'cmd': None},
	'MSYS/': {},
	'TOOL PATH/': {},
	'TLDATA/': {},
	'LOAD/': {},
	'GOTO/': {},
	'FEDRAT/': {},
	'PAINT/': {},
	'END-OF-PATH': {},
}


def read_cls_cut_file(file_path):
	# TODO: Force designers to output ISO formatted CLSs
	# TODO: Force designers to output CLS in metric (mm)
	"""Convert a cls(f) cut file to a list of CutCmds"""
	# "		CLSF		CUT					RULE
	# 	Filename	header				if CLSF does not start with $$CUT header then add header as file name. header translated as $$CUT to CLSF.
	# 	GOTO/GOHOME/FROM		line5b				GOTO translated to line5b based on the previous position.
	# 	NOTE: GOHOME is return home, but for now handle same as GOTO.
	# 	TOOL PATH	phase
	# 	LOAD/TOOL	cutter
	# 	FEDRAT		speed
	# 	$$			comment
	# 	$$CUT		all other commands
	# 	other		comment CLSF
	# 	END-OF-PATH	pass"
	# TODO: need to construct header from file name, date & time
	with open(file_path, 'r') as f:
		cmd_list = []
		tf = np.eye(4)
		prev_pt, prev_dir = None, None

		for line in f:
			cmd = None
			# TODO: will the stripping  line affect comments?
			line = line.strip()
			if line.startswith('$$ '):
				comment = line.lstrip('$$ ')
				cmd = CommentCmd([comment])
			elif line.startswith('$$CUT '):
				cut_line = line.replace('$$CUT ', '', 1)
				cmd = parse_ascii_cut_line(cut_line)
			elif line.startswith('MSYS/'):
				str_vals = line.split('MSYS/')[1].split(',')
				vals = list(map(float, str_vals))
				t = np.array(vals[:3])
				xr = np.array(vals[3:6])
				yr = np.array(vals[6:9])
				zr = np.cross(xr, yr)
				tf[:3, 0] = xr
				tf[:3, 1] = yr
				tf[:3, 2] = zr
				tf[:3, 3] = t
				comment = 'CLSF %s' % line
				cmd = CommentCmd([comment])
			elif line.startswith('TOOL PATH/'):
				line_items = line.split(',')
				phase_name = line_items[0].split('/')[1]
				cmd = PhaseCmd([phase_name])
				cmd.set_cutter(line_items[-1])
			elif line.startswith('LOAD/TOOL'):
				tool = line.split(',')[1]
				cmd = CutterCmd([tool])
			elif line.startswith('FEDRAT/'):
				line_list = line.split(',')
				if line_list[0].endswith('MMPM'):
					conv = 1/60000
				elif line_list[0].endswith('IPM'):
					conv = 25.4/60000
				else:
					raise ValueError('Unrecognized FEDRAT unit')
				spd = conv * float(line_list[1])
				cmd = SpeedCmd([spd])
			# elif line.startswith('END-OF-PATH'):
			# 	continue
			elif line.startswith('GOTO/'):
				str_vals = line.split('GOTO/')[1].split(',')
				# TODO: what precision to use when reading floats in?
				vals = list(map(float, str_vals))
				new_pt = np.array(vals[:3])
				new_ori = -1 * np.array(vals[3:6])  # Tool direction vector must be flipped to accomodate TCAT convention
				if prev_pt is None and prev_dir is None:
					cmd_list.append(OrientCmd([new_ori]))
					cmd_list.append(PointCmd([new_pt]))
				else:
					# TODO: what if user wants line instead of line5b?
					cmd = Line5XCmd([prev_pt, new_pt, prev_dir, new_ori])
				prev_pt = new_pt
				prev_dir = new_ori
			else:
				comment = 'CLSF %s' % line
				cmd = CommentCmd([comment])

			if cmd is not None:
				cmd_list.append(cmd)
	# for cmd in cmd_list:
	# 	print(cmd)
	return cmd_list


def is_cmd_list(lst, raise_err=True):
	if not isinstance(lst, list):
		if raise_err:
			raise TypeError('A command list must be a list.')
		else:
			return False

	for cmd in lst:
		if not isinstance(cmd, CutCmd):
			if raise_err:
				raise TypeError('%s is not a CutCmd.' % cmd)
			else:
				return False

	return True


def read_cut_file(file_path):
	# TODO: Should Error be raised if file isn't cut file? Or just Warning?
	if is_file(file_path):
		file_path = os.path.abspath(file_path)

	if is_cut_file(file_path):
		if is_cut_file_name(file_path):
			return read_ascii_cut_file(file_path)
		elif is_cbf_file_name(file_path):
			return read_binary_cut_file(file_path)
		elif is_cls_file_name(file_path):
			return read_cls_cut_file(file_path)
		else:
			raise RuntimeError('File is a cut file but could not be read in.')
	else:
		raise RuntimeError('File \'%s\' is not a CUT/CBF/CLS file.' % file_path)


def make_cbf_header(hdr_cmd, file_checksum, version, num_cmds, hdr_ext=None):
	# TODO: double check that file checksum is correct
	if not isinstance(hdr_cmd, HeaderCmd):
		raise RuntimeError('hdr_cmd must be a Header command.')

	hdr_ext_value = get_reserved_bytes(34)
	if hdr_ext is not None and isinstance(hdr_ext, HeaderExtCmd):
		hdr_ext_value = hdr_ext.get_cbf_value()

	start_pattern = hdr_cmd.get_cbf_cmd_code()
	end_pattern = 0xFFFFFFFF - start_pattern

	arg_bytes_list = [get_reserved_bytes(6),
	                   u_int_to_bytes(version, 2),
	                   hdr_cmd.get_cbf_value(),
	                   hdr_ext_value,
	                   u_int_to_bytes(num_cmds, 2),
	                   u_int_to_bytes(end_pattern, 4)]

	checksum = compute_checksum(b''.join(arg_bytes_list))
	hdr_checksum = u_int_to_bytes(checksum, 2)
	arg_bytes_list.insert(0, hdr_checksum)
	arg_bytes = b''.join(arg_bytes_list)
	file_checksum += compute_checksum(arg_bytes)
	hdr = [u_int_to_bytes(start_pattern, 4),
	       u_int_to_bytes(file_checksum, 4),
	       arg_bytes]

	return b''.join(hdr)


def make_goto_cmd(loc, ori, decimals=4):
	return 'GOTO/%s,%s' % (np_vec_to_cls_vec(loc, decimals),
	                       np_vec_to_cls_vec(ori, decimals))




