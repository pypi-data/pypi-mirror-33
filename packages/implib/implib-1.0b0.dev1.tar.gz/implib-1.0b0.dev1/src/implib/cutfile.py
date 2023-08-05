from time import strftime

from . import __version__
from .cutfileutils import *
from .fileutils import *
from .mathext import *
from .cutcmds import HeaderCmd, HeaderExtCmd, PointCmd, OrientCmd, Line5XCmd, MoveCmd, InfoCmd
# TODO: should probably just import __all__ from cutcmds

__all__ = ['CutFile']


# TODO: add logger

class CutFile:

	def __init__(self, cmd_list=None, name=None, version=3):
		# TODO: Add doc string
		# TODO: Will error out if cmd_list isn't properly formatted
		if cmd_list is None:
			self._cmds = []
		elif is_cmd_list(cmd_list):
			self._cmds = cmd_list

		self._read_file_path = None
		self._name = '' if name is None or not isinstance(name, str) else name
		self.version = version

	def read(self, file_path):
		self.set_cmd_list(read_cut_file(file_path))
		self._read_file_path = file_path
		self._name = get_file_name(file_path, exclude_ext=True)

	def write(self, dir_path=None, file_name=None, cut=False, cbf=False, cls=False):
		if dir_path is None:
			if self._read_file_path is None:
				# TODO: this might actually be fine, just means file never read.
				raise RuntimeError('Failed to infer directory path.')
			else:
				dir_path = get_dir(self._read_file_path)

		ext = None
		if file_name is None:
			if self._name is None:
				raise RuntimeError('Failed to infer file name.')
			else:
				file_name = self._name
				if self._read_file_path is not None:
					ext = get_ext(self._read_file_path)
		else:
			if has_ext(file_name):
				ext = get_ext(file_name)

		if ext is not None:
			# TODO: think this will fail if file_name has ext
			temp_fname = file_name + ext
			if is_cut_file_name(temp_fname):
				cut = True
			if is_cbf_file_name(temp_fname):
				cbf = True
			if is_cls_file_name(temp_fname):
				cls = True

		if cut or cbf or cls:
			self.set_header(self._name)

		if cut:
			file_path = make_file_name(dir_path, file_name, 'CUT', ext_upper=True)
			with open(file_path, 'w') as f:
				for cmd in self._cmds:
					f.write(cmd.get_cut() + '\n')
		if cbf:
			file_path = make_file_name(dir_path, file_name, 'cbf')
			if len(self._cmds) > 0 and isinstance(self._cmds[0], HeaderCmd):  # TODO: this should always be true now after calling set_header.
				hdr_ext = len(self._cmds) > 1 and isinstance(self._cmds[1], HeaderExtCmd)
				cmd_start_idx = 2 if hdr_ext else 1

				with open(file_path, 'wb') as f:
					checksum, num_cmds = 0, 0
					f.seek(128)  # leave room for the header
					for cmd in self._cmds[cmd_start_idx:]:
						cmd_bytes = cmd.get_cbf()
						checksum += compute_checksum(cmd_bytes)
						cmd_bytes = u_int_to_bytes(num_cmds, 2) + cmd_bytes
						f.write(cmd_bytes)
						num_cmds += 1
					f.seek(0)  # go back to beginning to fill in header
					hdr_ext = self._cmds[1] if hdr_ext else None
					hdr_bytes = make_cbf_header(self._cmds[0],
					                            checksum,
					                            self.version,
					                            num_cmds,
					                            hdr_ext)
					f.write(hdr_bytes)
		if cls:
			file_path = make_file_name(dir_path, file_name, 'cls')
			# TODO: need to call set_cutter for each phase command
			with open(file_path, 'w') as f:
				loc, ori = None, None
				for cmd in self._cmds:
					if isinstance(cmd, PointCmd):
						loc = cmd.start_pt
						if loc is not None and ori is not None:
							f.write(make_goto_cmd(loc, ori) + '\n')
					elif isinstance(cmd, OrientCmd):
						ori = -1 * cmd.start_dir
						if loc is not None and ori is not None:
							f.write(make_goto_cmd(loc, ori) + '\n')
					elif isinstance(cmd, Line5XCmd):
						loc = cmd.start_pt
						ori = -1 * cmd.start_dir
						f.write(make_goto_cmd(loc, ori) + '\n')
						loc = cmd.end_pt
						ori = -1 * cmd.end_dir
						f.write(make_goto_cmd(loc, ori) + '\n')
					else:
						f.write(cmd.get_cls() + '\n')

	def set_header(self, implant_pn):
		time_stamp = strftime('%x %X')
		pkg_ver = __version__
		cut_file_ver = self.version
		args = '%s CUT:%s ImpLib:%s date:%s' % (implant_pn,
		                                        cut_file_ver,
		                                        pkg_ver,
		                                        time_stamp)
		hdr = HeaderCmd([args])

		if isinstance(self._cmds[0], HeaderCmd):
			del self._cmds[0]
		self._cmds.insert(0, hdr)

	def get_name(self):
		return self._name

	def set_name(self, name):
		pass

	def get_cmd_list(self):
		# TODO: add cmd filter to get_cmd_list
		return self._cmds

	def set_cmd_list(self, cmd_list):
		if is_cmd_list(cmd_list, raise_err=False):
			self._cmds = cmd_list
		else:
			# TODO: what to do when cmd_list isn't a command list?
			pass

	def equals(self, other, hdr=True, moves=True, info=True):
		if not isinstance(other, self.__class__):
			return False

		other_cmds = other.get_cmd_list()
		if len(self._cmds) == 0 and len(other_cmds) == 0:
			return True

		if hdr:
			# TODO: add filter to get_cmd_list()
			this_hdr_chunk = [cmd for cmd in self._cmds
			                  if isinstance(cmd, HeaderCmd)
			                  or isinstance(cmd, HeaderExtCmd)]
			other_hdr_chunk = [cmd for cmd in other_cmds
			                   if isinstance(cmd, HeaderCmd)
			                   or isinstance(cmd, HeaderExtCmd)]
			if len(this_hdr_chunk) != len(other_hdr_chunk):
				return False
			for i in range(len(this_hdr_chunk)):
				if this_hdr_chunk[i] != other_hdr_chunk[i]:
					return False

		if moves:
			this_move_chunk = [cmd for cmd in self._cmds if isinstance(cmd, MoveCmd)]
			other_move_chunk = [cmd for cmd in other_cmds if isinstance(cmd, MoveCmd)]
			if len(this_move_chunk) != len(other_move_chunk):
				return False
			for i in range(len(this_move_chunk)):
				if this_move_chunk[i] != other_move_chunk[i]:
					return False

		if info:
			this_info_chunk = [cmd for cmd in self._cmds if isinstance(cmd, MoveCmd)]
			other_info_chunk = [cmd for cmd in other_cmds if isinstance(cmd, MoveCmd)]
			if len(this_info_chunk) != len(other_info_chunk):
				return False
			for i in range(len(this_info_chunk)):
				if this_info_chunk[i] != other_info_chunk[i]:
					return False

		return True

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			if len(self._cmds) != len(other._cmds):
				return False
			for i in range(len(self._cmds)):
				if self._cmds[i] != other._cmds[i]:
					return False
			return True
		return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result

	def connect_path(self):
		"""Fill in missing points/orients."""
		pass

	def check_path_continuity(self, error=True):
		"""Verify that the cut-path is continuous (no gaps in start/end points."""
		return False

	def get_pose_list(self, check_continuity=False):
		# TODO: update :class:`CutFile`.check_path_continuity doc string to include link to function.
		"""Convert movement commands to a list of goal-points.

		Calls :class:`MoveCmd`.get_end_pose() for all movement commands.
		
		Args:
		 	check_continuity (bool): execute :class:`CutFile`.check_path_continuity if True. Default is False
		
		Returns:
			numpy.array(): [list[x, y, z, a, b, c]]

		Notes:
			- x, y, z, a, b, and c are None by default.
			- returns numpy.array([]) (empty numpy array) if check_continuity()
			returns False.
		"""
		if check_continuity:
			if not self.check_path_continuity(error=False):
				return np.array([])

		poses = []
		for cmd in self._cmds:
			if isinstance(cmd, MoveCmd):
				# TODO: this is an issue for discontinuous paths
				poses.append(cmd.get_end_pose())

		return np.array(poses)
