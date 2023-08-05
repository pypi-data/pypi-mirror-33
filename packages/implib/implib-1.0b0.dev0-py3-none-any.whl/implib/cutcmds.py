"""This module is a collection of classes used to represent cut commands.

THINK uses three cut-file types: CLS, CUT, and CBF. While each file type has its
own formatting rules, they can all be used to represent the same list of commands.
Equivalency issues often arise when a command has multiple representations,
possibly a different model for each file type. This module ensures that there is
a single model for each command, and thus should prevent equivlanecy issues.

There are two main types of cut commands: :class:`MoveCmd` and :class:`InfoCmd`.

Notes:
	Default Units (unless specified otherwise): 
		- distance (mm)
		- velocity (m/s)
		- acceleration (m/s/s)
	Cut-file Format Spec Documents:
		- CBF :download:`300071, Rev03, Spec, Cutfile Binary Format (CBF) <specs/300071 Rev03 Spec, Cutfile Binary Format (CBF).pdf>`
		- CUT :download:`300072, Rev07, Spec, Cutfile ASCII Format (CUT) <specs/300072 Rev07 Spec Cutfile ASCII Format (CUT).pdf>`
		- CLS :download:`300319, Rev01, CLSFCUT Interface Specification <specs/300319 Rev01 CLSFCUT Interface Specification.pdf>`
		
.. moduleauthor:: C.J. Geering <cgeering@thinksurgical.com>

"""
# import numpy as np  # For all numpy 3-vectors, indices [0,1,2] --> [x,y,z] in R^3
from .mathext import *
from .cutter import CUTTERS

__all__ = ['CutCmd', 'MoveCmd', 'InfoCmd', 'PointCmd', 'OrientCmd',
           'Orient5XCmd', 'LineCmd', 'Line5XCmd', 'HeaderCmd', 'HeaderExtCmd',
           'CheckpointCmd', 'CutterCmd', 'PhaseCmd', 'StartshapeCmd',
           'EndshapeCmd', 'DecelOnCmd', 'DecelOffCmd', 'SpeedCmd', 'AccelCmd',
           'CutterOnCmd', 'CutterOffCmd', 'FCparmsCmd', 'VersionCmd',
           'CommentCmd', 'CheckSumCmd', 'InvalidCutCmdError']

# TODO: Add docstrings
# TODO: rewrite eq method to be general by iterating through class attributes
# and looking up type.
# TODO: Let tol be set in a config file.
# TODO: sort through class attributes and start making the proper fields private
# TODO: Comparing tol is different than decimal places to write to.
# TODO: Generalize _compile_cut_cmd. Particularly, get rid of ' '.join().
# TODO: specify units in docs (i.e. m/s, m, s)


class CutCmd(object):
	"""General cut command. 
	
	Base-class for all cut commands -- all cut commands must extend this class. 
	
	Args:
		arg_list (List, optional): A list of argument values. Defaults to None.
	
	Attributes:
		is_move_cmd (bool): True if this command is a MoveCmd.
		is_info_cmd (bool): True if this command is an InfoCmd.
		req_chkpt_before (bool): True if this command requries a checkpoint as the previous command.
		req_chkpt_after (bool): True if this command requries a checkpoint as the next command.
		req_stop_before (bool): True if all movement must be stopped before this command. 
		req_stop_after (bool): True if all movement must be stopped at the end of this command.
		
	Notes:
		- Default tolerance for all operations is 1e-4.
		
	"""
	is_move_cmd = False
	is_info_cmd = False
	req_chkpt_before = False
	req_chkpt_after = False
	req_stop_before = False
	req_stop_after = False
	_title = 'GEN_CMD'
	_cut_cmd_name = NotImplemented
	_cbf_cmd_code = NotImplemented
	_cbf_num_arg_bytes = NotImplemented
	_cls_cmd_name = NotImplemented
	_cmp_tol = 1e-4

	def __init__(self, arg_list=None):
		if arg_list is not None and not isinstance(arg_list, list):
				raise TypeError('arg_list must be a List or None')
		arg_list = [] if arg_list is None else arg_list
		self._arg_list = arg_list

	def __repr__(self):
		return self._title

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self._arg_list == other._arg_list
		return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result

	def _compile_cut_value(self):
		return NotImplemented

	def _compile_cbf_args(self):
		return NotImplemented

	def get_cbf(self):
		"""Compile and retrieve the CBF byte-string for this commmand. 
		
		The command is compiled according to the format specified in document
		:download:`300071, Rev03, Spec, Cutfile Binary Format (CBF) 
		<specs/300071 Rev03 Spec, Cutfile Binary Format (CBF).pdf>`. The
		returned bytearray will not include the command sequence number.
		
		Returns:
			bytearray: [cmd code, cmd code, # arg bytes, 0, checksum, args]
			
		Note:
			The returned bytearray will not include the command sequence number.	

		"""
		# TODO: add version as an optional input parameter
		arg_list = self._compile_cbf_args()
		arg_bytes = b''.join(arg_list)
		checksum = compute_checksum(arg_bytes)
		cmd_bytes = struct.pack('BBBBH',
		                        self._cbf_cmd_code,
		                        self._cbf_cmd_code,
		                        self._cbf_num_arg_bytes,
		                        0,
		                        checksum)
		return cmd_bytes + arg_bytes

	def get_cbf_cmd_code(self):
		"""Get the CBF command code for this command.
		
		The command codes are listed in document :download:`300071, Rev03, Spec,
		Cutfile Binary Format (CBF) <specs/300071 Rev03 Spec, Cutfile Binary Format (CBF).pdf>`.
		
		Returns:
			int: CBF command code

		"""
		return self._cbf_cmd_code

	def get_cut(self):
		"""Compile and retrieve the CUT command for this command.
		
		The command is compiled according to the format specified in document
		:download:`300072, Rev07, Spec, Cutfile ASCII Format (CUT) 
		<specs/300072 Rev07 Spec Cutfile ASCII Format (CUT).pdf>`.
		
		Returns:
			string: the CUT command (command name + command value)

		"""
		# TODO: put ' '.join here
		cmd_value = self._compile_cut_value()
		if cmd_value == '' or cmd_value is None:
			return self._cut_cmd_name
		else:
			return self._cut_cmd_name + ' ' + cmd_value

	def get_cls(self):
		"""Compile and retrieve the CLS command for this command.
		
		The command is compiled according to the format specified in document
		:download:`300319, Rev01, CLSFCUT Interface Specification
		<specs/300319 Rev01 CLSFCUT Interface Specification.pdf>`.
		
		Returns:
			string: the CLS command (for most commands this is the CUT command
			with "$$CUT" prepended to it)
		"""
		return '$$CUT %s' % self.get_cut()


class MoveCmd(CutCmd):
	"""Parent class for all Movement commands.
	
	Attributes:
		is_move_cmd (bool): True 
		
	Note:
		Default constructor will not assign any start/end points/directions.
	"""
	is_move_cmd = True
	_title = 'GEN_MOVE_CMD'
	# TODO: add fcparms as an attribute

	def __init__(self, arg_list=None):
		super().__init__(arg_list)
		# This is to initialize all points to None.
		# It wont actually set any points if MoveCmd is instantiated.
		self.start_pt = None  #: numpy 3-vec to store start point. Default is None.
		self.end_pt = None  #: numpy 3-vec to store end point. Default is None.
		self.start_dir = None  #: numpy 3-vec to store start direction. Default is None.
		self.end_dir = None  #: numpy 3-vec to store end direction. Default is None.

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			self_vecs = self._get_vecs()
			other_vecs = other._get_vecs()
			for i in range(len(self_vecs)):
				if not cmp_vec(self_vecs[i], other_vecs[i], self._cmp_tol):
					return False
			return True
		return NotImplemented

	def __repr__(self):
		repr_val = '%s:\n\t' % self._title
		if self.start_pt is not None:
			repr_val += 'start_pt: %s\n\t' % self.start_pt
		if self.end_pt is not None:
			repr_val += 'end_pt: %s\n\t' % self.end_pt
		if self.start_dir is not None:
			repr_val += 'start_dir: %s\n\t' % self.start_dir
		if self.end_dir is not None:
			repr_val += 'end_dir: %s\n\t' % self.end_dir
		return repr_val

	def _get_vecs(self):
		# Order matters
		return [vec for vec in [self.start_pt, self.end_pt, self.start_dir,
		                        self.end_dir] if vec is not None]

	def _compile_cut_value(self):
		return ' '.join(list(map(np_vec_to_cut_vec, self._get_vecs())))

	def _compile_cbf_args(self):
		return [np_vec_to_bytes(vec) for vec in self._get_vecs()]

	def get_cls(self):
		"""Over-ride CutCmd.get_cls().
		
		Returns:
			error: NotImplemented
			
		Note:
			This function over-rides the get_cls() function for the CutCmd class.
		"""
		return NotImplemented

	def get_start_pose(self):
		"""Retrieve the start point and start orientation.
		
		Returns:
			numpy-array: [x, y, z, a, b, c]
			
		Note:
			- If :attribute:`start_pt` is None then x=y=z=None.
			- If :attribute:`start_dir` is None then a=b=c=None.
		"""
		pt = [None, None, None] if self.start_pt is None else list(self.start_pt)
		dir = [None, None, None] if self.start_dir is None else list(self.start_dir)
		return np.array(pt + dir)

	def get_end_pose(self):
		"""Retrieve the end (goal) point and end (goal) orientation.

		Returns:
			numpy-array: [x, y, z, a, b, c]

		Note:
			- If :attribute:`end_pt` is None then x=y=z=None.
			- If :attribute:`end_dir` is None then a=b=c=None.
		"""
		pt = [None, None, None] if self.end_pt is None else list(self.end_pt)
		dir = [None, None, None] if self.end_dir is None else list(self.end_dir)
		return np.array(pt + dir)


class PointCmd(MoveCmd):
	"""Point movement command class
	
	"""
	_title = 'POINT'
	_cut_cmd_name = 'point'
	_cbf_cmd_code = 0x33
	_cbf_num_arg_bytes = 12

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.end_pt = arg_list[0]

	def __repr__(self):
		return '%s:\n\tgoal_point: %s' % (self._title, self.end_pt)


class OrientCmd(MoveCmd):
	_title = 'ORIENT'
	_cut_cmd_name = 'orient'
	_cbf_cmd_code = 0x58
	_cbf_num_arg_bytes = 24

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.end_dir = arg_list[0]

	def __repr__(self):
		return '%s:\n\tgoal_dir: %s' % (self._title, self.end_dir)

	# TODO: defined for Orient because of stupid reserved bytes...
	def _compile_cbf_args(self):
		return [np_vec_to_bytes(self.end_dir), get_reserved_bytes(12)]


class Orient5XCmd(MoveCmd):
	_title = 'ORIENT5X'
	_cut_cmd_name = 'orient5b'
	_cbf_cmd_code = 0x59
	_cbf_num_arg_bytes = 24

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_dir = arg_list[0]
		self.end_dir = arg_list[1]


class LineCmd(MoveCmd):
	_title = 'LINE'
	_cut_cmd_name = 'line'
	_cbf_cmd_code = 0xB6
	_cbf_num_arg_bytes = 24

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_pt = arg_list[0]
		self.end_pt = arg_list[1]

# TODO: Should movement commands have a length check on init args?
# TODO: Should movement commands have a type check on init args?


class Line5XCmd(MoveCmd):
	_title = 'LINE5X'
	_cut_cmd_name = 'line5b'
	_cbf_cmd_code = 0xB7
	_cbf_num_arg_bytes = 48

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_pt = arg_list[0]
		self.end_pt = arg_list[1]
		self.start_dir = arg_list[2]
		self.end_dir = arg_list[3]


class InfoCmd(CutCmd):
	is_info_cmd = True
	_title = 'GEN_INFO_CMD'


class HeaderCmd(InfoCmd):
	_title = 'HEADER'
	_cut_cmd_name = 'header'
	_cbf_cmd_code = 0x53A1B792
	_cbf_num_arg_bytes = 128

	# TODO: break up header into fields
	def __init__(self, arg_list):
		super().__init__(arg_list)
		data = arg_list[0].split()
		self.file_name = data[0]
		self.info = data[1:]
	# self.date = self.data[1]
	# self.time = self.data[2]

	def __repr__(self):
		return '%s:\n\tfile_name: %s\n\tinfo: %s' % (self._title, self.file_name, self.info)
	# return '%s:\n\tfile_name: %s\n\tdate: %s\n\ttime: %s' % (self._title, self.file_name, self.date, self.time)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.file_name == other.file_name and self.info == other.info
		# This could be problematic because this implies exact date and time are same.
		return NotImplemented

	def _compile_cut_value(self):
		return ' '.join([self.file_name, ' '.join(self.info)])

	def get_cbf_value(self):
		return str_to_bytes(self._compile_cut_value(), 70)


class HeaderExtCmd(InfoCmd):
	_title = 'HEADEREXT'
	_cut_cmd_name = 'header_ext'

	def get_cbf_value(self):
		return NotImplemented


class CheckpointCmd(InfoCmd):
	_title = 'CHECKPOINT'
	_cut_cmd_name = 'checkpoint'
	_cbf_cmd_code = 0x3C
	_cbf_num_arg_bytes = 32

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]
		self.recovery_pt = arg_list[1]
		# TODO: Add check to make sure per_comp is positive? If so, add test as well.
		self.per_comp = float(arg_list[2])

	def __repr__(self):
		return '%s:\n\tname: %s\n\trecovery_pt: %s\n\tpercent_comp: %s' \
		       % (self._title, self.name, self.recovery_pt, self.per_comp)

	def __eq__(self, other):
		# TODO: Should we be checking if name is equal?
		if isinstance(other, self.__class__):
			result = cmp_vec(self.recovery_pt, other.recovery_pt, self._cmp_tol) and \
			         cmp_flt(self.per_comp, other.per_comp, self._cmp_tol) and \
			         self.name == other.name
			return result
		return NotImplemented

	def _compile_cut_value(self):
		val_list = [self.name, np_vec_to_cut_vec(self.recovery_pt, decimals=4),
		            float_to_cut_string(self.per_comp, decimals=4)]
		return ' '.join(val_list)

	def _compile_cbf_args(self):
		return [str_to_bytes(self.name, 16), np_vec_to_bytes(self.recovery_pt),
		        float_to_bytes(self.per_comp)]


class CutterCmd(InfoCmd):
	_title = 'CUTTER'
	_cut_cmd_name = 'cutter'
	_cbf_cmd_code = 0xA3
	_cbf_num_arg_bytes = 32

	def __init__(self, arg_list):
		super().__init__(arg_list)
		pn = arg_list[0]
		if pn not in CUTTERS:
			raise RuntimeError('Cutter \'%s\' is not a valid Cutter.' % pn)
		self.cutter = CUTTERS[pn]

	def __repr__(self):
		return '%s:\n\tname: %s' % (self._title, self.cutter.part_number)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.cutter == other.cutter
		return NotImplemented

	def _compile_cut_value(self):
		# TODO: should decimals be set to 4?
		val_list = [self.cutter.part_number,
		            float_to_cut_string(self.cutter.length, decimals=4),
		            float_to_cut_string(self.cutter.radius, decimals=4),
		            float_to_cut_string(self.cutter.height, decimals=4)]
		return ' '.join(val_list)

	def _compile_cbf_args(self):
		return [str_to_bytes(self.cutter.part_number, 16),
		        float_to_bytes(self.cutter.length),
		        float_to_bytes(self.cutter.radius),
		        float_to_bytes(self.cutter.height),
		        get_reserved_bytes(4)]

	def get_cls(self):
		return 'LOAD/TOOL,%s' % self.cutter.part_number


class PhaseCmd(InfoCmd):
	_title = 'PHASE'
	_cut_cmd_name = 'phase'
	_cbf_cmd_code = 0x21
	_cbf_num_arg_bytes = 16

	# TODO: should there be format checks on name on init?
	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]
		self.cutter = None

	def __repr__(self):
		return '%s:\n\tname: %s' % (self._title, self.name)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.name == other.name
		return NotImplemented

	def set_cutter(self, cutter_pn):
		self.cutter = CUTTERS[cutter_pn]

	def _compile_cut_value(self):
		# TODO: should there be data type/format checking here?
		return self.name

	def _compile_cbf_args(self):
		return [str_to_bytes(self.name, 16)]

	def get_cls(self):
		# TODO: This is a hack to make sure each "TOOL PATH" command has a cutter.
		cutter_pn = '123456' if self.cutter is None else self.cutter.part_number
		return 'TOOL PATH/%s,TOOL,%s' % (self.name, cutter_pn)


class ShapeCmd(InfoCmd):
	_cbf_num_arg_bytes = 6

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]
		self.num_moves = arg_list[1]

	def __repr__(self):
		return '%s:\n\tname: %s\n\tnum_moves: %s' % (self._title, self.name, self.num_moves)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.name == other.name and self.num_moves == other.num_moves \
			       and self._title == other._title
		return NotImplemented

	def _compile_cut_value(self):
		return '%s %d' % (self.name, self.num_moves)

	def _compile_cbf_args(self):
		return [str_to_bytes(self.name, 5), u_int_to_bytes(self.num_moves, 1)]


class StartshapeCmd(ShapeCmd):
	_title = 'START_SHAPE'
	_cut_cmd_name = 'startshape'
	_cbf_cmd_code = 0xC9


class EndshapeCmd(ShapeCmd):
	_title = 'END_SHAPE'
	_cut_cmd_name = 'endshape'
	_cbf_cmd_code = 0x65


class DecelCmd(InfoCmd):
	_cbf_num_arg_bytes = 0

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented

	def _compile_cut_value(self):
		return None

	def _compile_cbf_args(self):
		return []


class DecelOnCmd(DecelCmd):
	_title = 'DECEL_ON'
	_cut_cmd_name = 'decel_on'
	_cbf_cmd_code = 0x4E


class DecelOffCmd(DecelCmd):
	_title = 'DECEL_OFF'
	_cut_cmd_name = 'decel_off'
	_cbf_cmd_code = 0x2B


class SpeedCmd(InfoCmd):
	_title = 'SPEED'
	_cut_cmd_name = 'speed'
	_cbf_cmd_code = 0x8B
	_cbf_num_arg_bytes = 4

	def __init__(self, arg_list):
		super().__init__(arg_list)
		# TODO: should arg_list[0] be cast to float?
		self.speed = arg_list[0]

	def __repr__(self):
		return '%s:\n\tspeed: %s' % (self._title, self.speed)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return cmp_flt(self.speed, other.speed, self._cmp_tol)
		return NotImplemented

	def _compile_cut_value(self):
		return float_to_cut_string(self.speed, decimals=4)

	def _compile_cbf_args(self):
		return [float_to_bytes(self.speed)]

	def get_cls(self):
		mps_to_mmps = 60000
		return 'FEDRAT/MMPM,%s' % float_to_cut_string(mps_to_mmps*self.speed, decimals=4)


class AccelCmd(InfoCmd):
	_title = 'ACCEL'
	_cut_cmd_name = 'accel'
	_cbf_cmd_code = 0x47
	_cbf_num_arg_bytes = 8

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.accel = arg_list[0]
		self.decel = arg_list[1]

	def __repr__(self):
		return '%s:\n\taccel: %s\n\tdecel: %s' % (self._title, self.accel, self.decel)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return cmp_flt(self.accel, other.accel, self._cmp_tol) and \
			       cmp_flt(self.decel, other.decel, self._cmp_tol)
		return NotImplemented

	def _compile_cut_value(self):
		return ' '.join([float_to_cut_string(self.accel, decimals=4),
		                 float_to_cut_string(self.decel, decimals=4)])

	def _compile_cbf_args(self):
		return [float_to_bytes(self.accel), float_to_bytes(self.decel)]


class CutterControlCmd(InfoCmd):
	_cbf_num_arg_bytes = 0

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented

	def _compile_cut_value(self):
		return None

	def _compile_cbf_args(self):
		return []


class CutterOnCmd(CutterControlCmd):
	_title = 'CUTTER_ON'
	_cut_cmd_name = 'cutter_on'
	_cbf_cmd_code = 0xBB


class CutterOffCmd(CutterControlCmd):
	_title = 'CUTTER_OFF'
	_cut_cmd_name = 'cutter_on'
	_cbf_cmd_code = 0x66


class FCparmsCmd(InfoCmd):
	_title = 'FC_PARMS'
	_cut_cmd_name = 'fcparms'
	_cbf_cmd_code = 0xFC
	_cbf_num_arg_bytes = 16

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.nominal_speed = arg_list[0]
		self.max_speed = arg_list[1]
		self.min_speed = arg_list[2]
		self.max_force = arg_list[3]

	def __repr__(self):
		return '%s:\n\tnominal_speed: %s\n\tmax_speed: %s\n\tmin_speed: %s\n\tmax_force: %s' \
		       % (self._title, self.nominal_speed, self.max_speed, self.min_speed, self.max_force)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			result = cmp_flt(self.nominal_speed, other.nominal_speed, self._cmp_tol) and \
			         cmp_flt(self.max_speed, other.max_speed, self._cmp_tol) and \
			         cmp_flt(self.min_speed, other.min_speed, self._cmp_tol) and \
			         cmp_flt(self.max_force, other.max_force, self._cmp_tol)
			return result
		return NotImplemented

	def _get_val_list(self):
		# Order matters
		return [self.nominal_speed, self.max_speed, self.min_speed, self.max_force]

	def _compile_cut_value(self):
		return ' '.join([float_to_cut_string(val, decimals=4) for val in self._get_val_list()])

	def _compile_cbf_args(self):
		return list(map(float_to_bytes, self._get_val_list()))


class VersionCmd(InfoCmd):
	_title = 'VERSION'
	_cbf_cmd_code = 0x55
	_cbf_num_arg_bytes = 32

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


class CommentCmd(InfoCmd):
	_title = 'COMMENT'
	_cut_cmd_name = 'comment'
	_cbf_cmd_code = 0x5A
	_cbf_num_arg_bytes = 40

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.text = arg_list[0]

	def __repr__(self):
		return '%s:\n\ttext: %s' % (self._title, self.text)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.text == other.text
		return NotImplemented

	def _compile_cut_value(self):
		# TODO: set string length limit?
		return self.text

	def _compile_cbf_args(self):
		return [str_to_bytes(self.text, 40)]

	def get_cls(self):
		if self.text.startswith('CLSF '):
			return self.text.replace('CLSF ', '', 1)
		else:
			return '$$ %s' % self.text


class CheckSumCmd(InfoCmd):
	_title = 'CHECK_SUM'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


# Cut Command Specific Exceptions


class InvalidCutCmdError(Exception):
	def __init__(self, cmd):
		msg = '%s is not a valid CUT command.' % cmd
		super().__init__(msg)
