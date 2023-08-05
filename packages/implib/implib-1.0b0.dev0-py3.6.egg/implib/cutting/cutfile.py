import os.path

from cutting.cutfileparsers import parse_ascii_cut_file, parse_binary_cut_file

__all__ = ['CutFile']

class CutFile:
	"""Universal Cut File Representation.
	
	Key Attributes:
	self.cmd_list -- list containing the CutCmd sequence.
	
	Key Methods:
	parse(self) -- converts standard cut file typesinto a CutCmd list.
	"""

	def __init__(self, path):
		"""Create a CutFile object. Do nothin else; no parsing, verifying, etc."""

		self.file_path = path
		# TODO: Make sure path is valid before being passed in. Don't need to check file ext.
		self.cmd_list = None  # self.parse()

	def parse(self, file_path=None):
		"""Parse CBF, CUT, or CLS and Return the CutCmd list. Filter function."""
		file_path = self.file_path if file_path is None else file_path
		ext = str(os.path.splitext(file_path)[1])[1:].lower()  # get ext, strip period, convert to lower.
		if ext == 'cut':
			self.cmd_list = parse_ascii_cut_file(file_path)
		elif ext == 'cbf':
			self.cmd_list = parse_binary_cut_file(file_path)
		# elif ext == 'cls':
		# 	self.cmd_list =
		else:
			raise ValueError('Unsupported Cut File type with file: %s. The supported Cut File types'
			                 'are: .CLS, .CUT, and .CBF.' % file_path)
		return self.cmd_list

	def show_cmd_list(self):
		for cmd in self.cmd_list:
			print(cmd)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			for i in range(len(self.cmd_list)):
				if self.cmd_list[i] != other.cmd_list[i]:
					return False
			return True
		return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result


if __name__ == '__main__':
	bin_fname = 'X:\Individual Folders\CJG\Laptop\THINK\Projects\CutFilePy\perTMCRELP.cbf'
	cut_fname = 'X:\Individual Folders\CJG\Laptop\THINK\Projects\CutFilePy\perTMCRELP.CUT'
	CF1 = CutFile(bin_fname)
	CF1.parse()
	CF2 = CutFile(cut_fname)
	CF2.parse()

	# print('CMD LST LEN: %s, %s' % (len(CF1.cmd_list), len(CF2.cmd_list)))
	print(CF1 == CF2)
