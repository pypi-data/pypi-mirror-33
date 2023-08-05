import pytest
import os.path
from implib.cutfile import *
from implib.cutcmds import *


class TestCutFileInit(object):

	def test_no_args(self):
		cf = CutFile()
		assert cf._cmds == []
		assert cf._read_file_path is None
		assert cf._name == ''

	def test_bad_cmd_list(self):
		bad_cmd_list = ['this is a bad cmd list because it is not a list',
		                [CutCmd(), 'not a cut command']]
		for cmd_list in bad_cmd_list:
			with pytest.raises(TypeError, message='TypeError Expected'):
				CutFile(cmd_list=cmd_list)

	def test_bad_name(self):
		bad_names = [12345, object]
		for bad_name in bad_names:
			cf = CutFile(name=bad_name)
			assert cf._name == ''

	def test_good_cmd_list(self):
		good_cmd_lists = [[],
		                  [CutCmd(), CutCmd()]]

		for cmd_list in good_cmd_lists:
			cf = CutFile(cmd_list=cmd_list)
			assert cf._cmds == cmd_list
			assert cf._read_file_path is None
			assert cf._name == ''


class TestCutFileGettersAndSetter(object):
	cf = CutFile(cmd_list=[], name='')

	# TODO: implement test_set_name
	# def test_set_name(self):
	# 	name = 'New CF name'
	# 	self.cf.set_name(name)
	# 	assert self.cf.

	def test_get_name(self):
		assert self.cf.get_name() == self.cf._name

	def test_get_cmd_list(self):
		assert self.cf.get_cmd_list() == self.cf._cmds

	def test_set_cmd_list(self):
		new_cmd_list = [CutCmd(), CutCmd(), CutCmd()]
		self.cf.set_cmd_list(new_cmd_list)
		assert self.cf.get_cmd_list() == new_cmd_list

		old_cmd_list = self.cf.get_cmd_list()
		new_cmd_list = 'this is not a valid cmd list because it is not a list'
		self.cf.set_cmd_list(new_cmd_list)
		assert self.cf.get_cmd_list() == old_cmd_list


class TestCutFileDefaults(object):
	cf1_no_cmd_list = CutFile(name='cf1')
	cf1 = CutFile(cmd_list=[CutCmd(), CutCmd()], name='cf1')
	cf2 = CutFile(cmd_list=[CutCmd(), CutCmd()], name='cf2')

	def test_equality(self):
		assert self.cf1 == self.cf2

	def test_inequality(self):
		assert self.cf1_no_cmd_list != self.cf1
		assert self.cf1_no_cmd_list != self.cf2

	# TODO: implement test for __repr__ and __str__ once these methods are implemented


# TODO: most of these tests should really be in test_cutfileutils
class TestCutFileRead(object):
	not_a_file_name = './tests/data/cut_files/this_is_a_directory/'
	file_does_not_exist = './tests/data/cut_files/this_file_does_not_exist.CUT'
	not_a_cut_file_name = './tests/data/cut_files/this_is_not_a_cut_file.txt'
	cbf_fname = './tests/data/cut_files/CBF/perTMCRELP.cbf'
	cut_fname = './tests/data/cut_files/CUT/perTMCRELP.CUT'
	CF = CutFile(name='CF1')

	def test_not_a_file(self):
		with pytest.raises(FileExistsError, message='File Exists Error Expected'):
			self.CF.read(self.not_a_file_name)
		with pytest.raises(FileExistsError, message='File Exists Error Expected'):
			self.CF.read(self.file_does_not_exist)

	def test_not_a_cut_file(self):
		with pytest.raises(RuntimeError):
			self.CF.read(self.not_a_cut_file_name)

	@pytest.mark.xfail
	def test_cut(self):
		assert 0

	@pytest.mark.xfail
	def test_cbf(self):
		assert 0

	@pytest.mark.xfail
	def test_cls(self):
		assert 0


class TestCutFileWrite(object):
	not_a_file_name = './tests/data/cut_files/this_is_a_directory/'
	file_does_not_exist = './tests/data/cut_files/this_file_does_not_exist.CUT'
	not_a_cut_file_name = './tests/data/cut_files/this_is_not_a_cut_file.txt'
	cbf_fname = './tests/data/cut_files/CBF/perTMCRELP_small.cbf'
	cut_fname = './tests/data/cut_files/CUT/perTMCRELP_small.CUT'
	cut_fname_test = 'perTMCRELP_small_test.CUT'
	cut_fname_test_no_ext = 'perTMCRELP_small_test'
	CF_not_read = CutFile(name='Not Read')
	CF_read = CutFile(name='Read')
	CF_test = CutFile(name='Tester')

	def test_no_args(self):
		pass

	def test_dir_path_not_none(self):
		pass

	def test_file_name_no_none(self):
		pass

	def test_cut(self):
		self.CF_read.read(self.cut_fname)
		self.CF_read.write(dir_path='./tests/data/cut_files/CUT',
		                   file_name=self.cut_fname_test)
		self.CF_test.read(os.path.join('./tests/data/cut_files/CUT', self.cut_fname_test))
		assert self.CF_read == self.CF_test
		self.CF_test.write(dir_path='./tests/data/cut_files/CUT',
		                   file_name=self.cut_fname_test_no_ext,
		                   cut=True)
		self.CF_test.read(os.path.join('./tests/data/cut_files/CUT', self.cut_fname_test))
		assert self.CF_read.equals(self.CF_test, hdr=False)

	def test_cbf(self):
		pass

	def test_cls(self):
		pass


class TestCutFileEquality(object):
	pass

if __name__ == '__main__':
	# cf1 = CutFile()
	# cut_fname = 'data/cut_files/CUT/perTMCRELP.CUT'
	# cf1.read(cut_fname)
	# cf1.write(dir_path='data/cut_files/CBF', file_name='just_for_testing', cbf=True)

	# cf2 = CutFile()
	# cf2.read('data/cut_files/CUT/just_for_testing.cbf')
	# cf2.write(file_name='cbf_as_cut', cut=True)
	#
	# hdr = HeaderCmd(['fname', 'd&t info'])
	# p1 = PointCmd([[2.9663, -34.6869, -2.4553]])
	# cmd_list = [hdr, p1]
	# cf = CutFile(cmd_list=cmd_list)
	# cf.write(dir_path='data/cut_files/CBF', file_name='just_for_testing', cbf=True)

	### CLS Testing
	cf1 = CutFile()
	cls1 = 'data/n802701lmet.cls'
	cf1.read(cls1)

	cut1 = 'data/n802701met_test'
	cf1.write(dir_path='data/', file_name=cut1, cut=True, cls=True)