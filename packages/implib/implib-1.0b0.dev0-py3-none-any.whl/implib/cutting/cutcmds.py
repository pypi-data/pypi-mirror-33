import numpy as np  # For all numpy 3-vectors, indices [0,1,2] --> [x,y,z] in R^3

from src.implib import cmp_vec, cmp_flt

__all__ = ['CutCmd', 'MoveCmd', 'InfoCmd', 'PointCmd', 'OrientCmd', 'Orient5XCmd', 'LineCmd', 'Line5XCmd', 'HeaderCmd',
           'HeaderExtCmd', 'CheckpointCmd', 'CutterCmd', 'PhaseCmd', 'StartshapeCmd', 'EndshapeCmd', 'DecelOnCmd',
           'DecelOffCmd', 'SpeedCmd', 'AccelCmd', 'CutterOnCmd', 'CutterOffCmd', 'FCparmsCmd', 'VersionCmd',
           'CommentCmd', 'CheckSumCmd', 'InvalidCutCmdError']

# TODO: Add docstrings
# TODO: rewrite eq method to be general by iterating through class attributes and looking up type.
# TODO: Let tol be set in a config file


class CutCmd:
	"""Cut Command Parent Class"""
	is_move_cmd = False
	is_info_cmd = False
	req_chkpt_before = False
	req_chkpt_after = False
	req_stop_before = False
	req_stop_after = False
	title = 'GEN_CMD'

	def __init__(self, arg_list=None):
		self.arg_list = arg_list
		# self.cut_cmd_name = CUT_CMD_TABLE[np.where(CUT_CMD_TABLE[:, 0]==self)[0][0], 1]

	def __repr__(self):
		return self.title

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.arg_list == other.arg_list
		return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result


class MoveCmd(CutCmd):
	is_move_cmd = True
	title = 'GEN_MOVE_CMD'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_pt, self.end_pt, self.start_dir, self.end_dir = None, None, None, None  # np.empty(3, dtype=float)

	# TODO: add fcparms as an attribute
	# TODO: call super.__eq__()
	def __eq__(self, other, tol=1e-4):
		if isinstance(other, self.__class__):
			result = cmp_vec(self.start_pt, other.start_pt, tol) and \
				cmp_vec(self.end_pt, other.end_pt, tol) and \
				cmp_vec(self.start_dir, other.start_dir, tol) and \
				cmp_vec(self.end_dir, other.end_dir, tol)
			return result
		return NotImplemented


class PointCmd(MoveCmd):
	title = 'POINT'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_pt = arg_list[0]

	def __repr__(self):
		return '%s:\n\tgoal_point: %s' % (self.title, self.start_pt)


class OrientCmd(MoveCmd):
	title = 'ORIENT'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_dir = arg_list[0]

	def __repr__(self):
		return '%s:\n\tgoal_dir: %s' % (self.title, self.start_dir)


class Orient5XCmd(MoveCmd):
	title = 'ORIENT5X'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_dir = arg_list[0]
		self.end_dir = arg_list[1]

	def __repr__(self):
		return '%s:\n\tstart_dir: %s\n\tend_dir: %s' % (self.title, self.start_dir, self.end_dir)


class LineCmd(MoveCmd):
	title = 'LINE'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_pt = arg_list[0]
		self.end_pt = arg_list[1]

	def __repr__(self):
		return '%s:\n\tstart_pt: %s\n\tend_pt: %s' % (self.title, self.start_pt, self.end_pt)


class Line5XCmd(MoveCmd):
	title = 'LINE5X'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.start_pt = arg_list[0]
		self.end_pt = arg_list[1]
		self.start_dir = arg_list[2]
		self.end_dir = arg_list[3]

	def __repr__(self):
		return '%s:\n\tstart_pt: %s\n\tend_pt: %s\n\tstart_dir: %s\n\tend_dir: %s'\
		       % (self.title, self.start_pt, self.end_pt, self.start_dir, self.end_dir)


class InfoCmd(CutCmd):
	is_info_cmd = True
	title = 'GEN_INFO_CMD'


class HeaderCmd(InfoCmd):
	title = 'HEADER'

	# TODO: break up header into fields
	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.data = arg_list[0].split()
		self.file_name = self.data[0]
		self.info = self.data[1:]
		# self.date = self.data[1]
		# self.time = self.data[2]

	def __repr__(self):
		return '%s:\n\tfile_name: %s\n\tinfo: %s' % (self.title, self.file_name, self.info)
		# return '%s:\n\tfile_name: %s\n\tdate: %s\n\ttime: %s' % (self._title, self.file_name, self.date, self.time)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.file_name == other.file_name and self.info == other.info
			# This could be problematic because this implies exact date and time are same.
		return NotImplemented


class HeaderExtCmd(InfoCmd):
	title = 'HEADEREXT'


class CheckpointCmd(InfoCmd):
	title = 'CHECKPOINT'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]
		self.recovery_pt = arg_list[1]
		self.per_comp = arg_list[2]

	def __repr__(self):
		return '%s:\n\tname: %s\n\trecovery_pt: %s\n\tpercent_comp: %s'\
		       % (self.title, self.name, self.recovery_pt, self.per_comp)

	def __eq__(self, other, tol=1e-4):
		if isinstance(other, self.__class__):
			result = cmp_vec(self.recovery_pt, other.recovery_pt, tol) and cmp_flt(self.per_comp, other.per_comp, tol)
			return result
		return NotImplemented


class CutterCmd(InfoCmd):
	title = 'CUTTER'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]
		self.length = arg_list[1]
		self.radius = arg_list[2]
		self.height = arg_list[3]

	def __repr__(self):
		return '%s:\n\tname: %s\n\tlength: %s\n\tradius: %s\n\theight: %s'\
		       % (self.title, self.name, self.length, self.radius, self.height)

	def __eq__(self, other, tol=1e-4):
		if isinstance(other, self.__class__):
			result = self.name == other.name and cmp_flt(self.length, other.length, tol) and \
			         cmp_flt(self.radius, other.radius, tol) and cmp_flt(self.height, other.height, tol)
			return result
		return NotImplemented


class PhaseCmd(InfoCmd):
	title = 'PHASE'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]

	def __repr__(self):
		return '%s:\n\tname: %s' % (self.title, self.name)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.name == other.name
		return NotImplemented


class StartshapeCmd(InfoCmd):
	title = 'START_SHAPE'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]
		self.num_moves = arg_list[1]

	def __repr__(self):
		return '%s:\n\tname: %s\n\tnum_moves: %s' % (self.title, self.name, self.num_moves)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.name == other.name and self.num_moves == other.num_moves
		return NotImplemented


class EndshapeCmd(InfoCmd):
	title = 'END_SHAPE'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.name = arg_list[0]
		self.num_moves = arg_list[1]

	def __repr__(self):
		return '%s:\n\tname: %s\n\tnum_moves: %s' % (self.title, self.name, self.num_moves)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.name == other.name and self.num_moves == other.num_moves
		return NotImplemented


class DecelOnCmd(InfoCmd):
	title = 'DECEL_ON'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


class DecelOffCmd(InfoCmd):
	title = 'DECEL_OFF'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


class SpeedCmd(InfoCmd):
	title = 'SPEED'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.speed = arg_list[0]

	def __repr__(self):
		return '%s:\n\tspeed: %s' % (self.title, self.speed)

	def __eq__(self, other, tol=1e-4):
		if isinstance(other, self.__class__):
			return cmp_flt(self.speed, other.speed, tol)
		return NotImplemented


class AccelCmd(InfoCmd):
	title = 'ACCEL'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.accel = arg_list[0]
		self.decel = arg_list[1]

	def __repr__(self):
		return '%s:\n\taccel: %s\n\tdecel: %s' % (self.title, self.accel, self.decel)

	def __eq__(self, other, tol=1e-4):
		if isinstance(other, self.__class__):
			return cmp_flt(self.accel, other.accel, tol) and cmp_flt(self.decel, other.decel, tol)
		return NotImplemented


class CutterOnCmd(InfoCmd):
	title = 'CUTTER_ON'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


class CutterOffCmd(InfoCmd):
	title = 'CUTTER_OFF'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


class FCparmsCmd(InfoCmd):
	title = 'FC_PARMS'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.nominal_speed = arg_list[0]
		self.max_speed = arg_list[1]
		self.min_speed = arg_list[2]
		self.max_force = arg_list[3]

	def __repr__(self):
		return '%s:\n\tnominal_speed: %s\n\tmax_speed: %s\n\tmin_speed: %s\n\tmax_force: %s'\
		       % (self.title, self.nominal_speed, self.max_speed, self.min_speed, self.max_force)

	def __eq__(self, other, tol=1e-4):
		if isinstance(other, self.__class__):
			result = cmp_flt(self.nominal_speed, other.nominal_speed, tol) and \
			       cmp_flt(self.max_speed, other.max_speed, tol) and cmp_flt(self.min_speed, other.min_speed, tol) and \
			       cmp_flt(self.max_force, other.max_force, tol)
			return result
		return NotImplemented


class VersionCmd(InfoCmd):
	title = 'VERSION'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


class CommentCmd(InfoCmd):
	title = 'COMMENT'

	def __init__(self, arg_list):
		super().__init__(arg_list)
		self.text = arg_list[0]

	def __repr__(self):
		return '%s:\n\ttext: %s' % (self.title, self.text)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.text == other.text
		return NotImplemented


class CheckSumCmd(InfoCmd):
	title = 'CHECK_SUM'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return True
		return NotImplemented


# Cut Command Specific Exceptions


class InvalidCutCmdError(Exception):
	def __init__(self, cmd):
		msg = '%s is not a valid CUT command!' % cmd
		super().__init__(msg)


# TODO: read this table in from a CSV.
CUT_CMD_TABLE = np.array([
	[HeaderCmd, 'header'],
	[HeaderExtCmd, 'header_ext'],
	[CheckpointCmd, 'checkpoint'],
	[CutterCmd, 'cutter'],
	[OrientCmd, 'orient'],
	[OrientCmd, 'orient5b'],
	[PhaseCmd, 'phase'],
	[StartshapeCmd, 'startshape'],
	[EndshapeCmd, 'endshape'],
	[DecelOffCmd, 'decel_off'],
	[DecelOnCmd, 'decel_on'],
	[PointCmd, 'point'],
	[LineCmd, 'line'],
	[LineCmd, 'line5b'],
	[SpeedCmd, 'speed'],
	[AccelCmd, 'accel'],
	[CutterOnCmd, 'cutter_on'],
	[CutterOffCmd, 'cutter_off'],
	[FCparmsCmd, 'fcparms'],
	[VersionCmd, 'version'],
	[CommentCmd, 'comment'],
	[CheckSumCmd, 'check_sum']
])


if __name__ == '__main__':
	pass