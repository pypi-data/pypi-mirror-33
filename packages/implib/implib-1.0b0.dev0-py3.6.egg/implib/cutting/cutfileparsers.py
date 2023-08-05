import re
import struct

from src.implib import *

__all__ = ['parse_cls_cut_file', 'parse_binary_cut_file', 'parse_ascii_cut_file']

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


# TODO: Add try-catch
def parse_ascii_cut_file(file_path):
	"""Convert an ASCII cut file to a list of CutCmds."""

	with open(file_path, 'r') as f:
		cmd_list = []
		num_lines = 0
		for line in f:
			num_lines += 1
			split_result = line.split()
			ascii_cmd = split_result[0]
			ascii_args = None if len(split_result) == 1 else line.split(' ', 1)[1]

			if ascii_cmd not in ASCII_CMD_TO_CUT_CMD.keys():
				raise InvalidCutCmdError(ascii_cmd)
			elif ASCII_CMD_TO_CUT_CMD[ascii_cmd]['args'] is None:
				cmd_list.append(ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd']())
			elif ascii_args is None:
				cmd_list.append(ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd']([None]))
			else:
				arg_list = []
				for arg_type in ASCII_CMD_TO_CUT_CMD[ascii_cmd]['args']:
					mo = ASCII_ARG_TYPE[arg_type]['re'].search(ascii_args)
					arg_list.append(ASCII_ARG_TYPE[arg_type]['conv_func'](mo))
					ascii_args = ascii_args[mo.span(0)[1]:]
				cmd_list.append(ASCII_CMD_TO_CUT_CMD[ascii_cmd]['cmd'](arg_list))

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
	'r': (lambda x: x)  # reserved byte
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
def parse_binary_cut_file(file_path):
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


def parse_cls_cut_file(file_path):
	"""Convert a cls(f) cut file to a list of CutCmds"""
	# "		CLSF		CUT					RULE
	# 	Filename	header				if CLSF does not start with $$CUT header then add header as file name. header translated as $$CUT to CLSF.
	# 	GOTO/GOHOME/FROM		line5b				GOTO translated to line5b based on the previous position.
	# 	NOTE: GOHOME is return home, but for now handle same as GOTO.
	# 	CIRCLE		arc5b
	# 	TOOL PATH	phase
	# 	LOAD/TOOL	cutter
	# 	FROM		point
	# 	FEDRAT		speed
	# 	$$			comment
	# 	$$CUT		all other commands
	# 	other		comment CLSF
	# 	END-OF-PATH	End of file"
	pass
