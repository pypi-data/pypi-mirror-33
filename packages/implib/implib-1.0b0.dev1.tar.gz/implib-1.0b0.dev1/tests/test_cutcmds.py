import pytest
import numpy as np
from implib.cutcmds import *
from implib.mathext import np_vec_to_cut_vec, float_to_cut_string
from implib.cutter import CUTTERS


# TODO: For all equality checking test methods, add statement to test that
# NotImplemented is returned when mismatched classes are equated.
# TODO: when checking get_cut, shouldn't use the mathext functions. Should use
# fancy print formatting.

"""General Command Tests"""


class TestCutCmd(object):

	def test_init(self):
		cmd = CutCmd(None)
		assert cmd._arg_list == []
		lst = [1.234, '1234', 1234]
		cmd = CutCmd(lst)
		assert cmd._arg_list == lst
		with pytest.raises(TypeError, message='TypeError Expected'):
			CutCmd('this will cause TypeError b/c string is not a List or None')


"""Movement Commands Tests"""


class TestMoveCmd(object):
	p1 = np.array([1., 1., 1.])
	p2 = np.array([2., 3., 4.])
	p3 = np.array([-1., -2., -3.])
	p4 = np.array([100., 1000., -10000.])
	arg_list1 = None
	arg_list2 = [p1, p2]
	arg_list3 = [p1, p2, p3]
	arg_list4 = [p1, p2, p3, p4]

	def test_init(self):
		init_arg_options = [self.arg_list1, self.arg_list2,
		                    self.arg_list3, self.arg_list4]
		for args in init_arg_options:
			cmd = MoveCmd(args)
			assert cmd.start_pt is None
			assert cmd.end_pt is None
			assert cmd.start_dir is None
			assert cmd.end_dir is None
			assert cmd.is_move_cmd
			assert not cmd.is_info_cmd

	def test_equality_and_inequality(self):
		cmd1 = MoveCmd(self.arg_list1)
		v1 = np.array([1., 1., 1.])
		cmd1.start_pt = v1
		cmd1.end_pt = v1
		cmd1.start_dir = v1
		cmd1.end_dir = v1

		cmd2 = MoveCmd(self.arg_list1)
		v2 = np.array([1.01, 1.01, 1.01])
		cmd2.start_pt = v2
		cmd2.end_pt = v2
		cmd2.start_dir = v2
		cmd2.end_dir = v2

		cmd3 = MoveCmd(self.arg_list1)
		v3 = np.array([1.000001, 1.000001, 1.000001])
		cmd3.start_pt = v3
		cmd3.end_pt = v3
		cmd3.start_dir = v3
		cmd3.end_dir = v3

		assert cmd1 == cmd1
		cmd1._cmp_tol = 1e-1  # tolerance = 1e-1
		assert cmd1 == cmd2
		cmd1._cmp_tol = 1e-5  # tolerance = 1e-5
		assert cmd1 == cmd3
		cmd1._cmp_tol = 1e-4  # tolerance back to 1e-4
		assert cmd1 != cmd2

	def test_get_vecs(self):
		cmd1 = MoveCmd(self.arg_list1)
		assert cmd1._get_vecs() == []
		v1 = np.array([1., 1., 1.])
		cmd1.start_pt = v1
		assert np.array_equal(cmd1._get_vecs(), [v1])
		cmd1.end_pt = 2 * v1
		assert np.array_equal(cmd1._get_vecs(), [v1, 2 * v1])
		cmd1.start_dir = 3 * v1
		assert np.array_equal(cmd1._get_vecs(), [v1, 2 * v1, 3 * v1])
		cmd1.end_dir = 4 * v1
		assert np.array_equal(cmd1._get_vecs(), [v1, 2 * v1, 3 * v1, 4 * v1])

	def test_compile_cut_value(self):
		cmd = MoveCmd(self.arg_list1)
		v = np.array([1.000001, 1.000001, 1.000001])
		cmd.start_pt = v
		cmd.end_pt = 2 * v
		cmd.start_dir = 3 * v
		cmd.end_dir = 4 * v
		expected_val = ' '.join([np_vec_to_cut_vec(v),
		                         np_vec_to_cut_vec(2 * v),
		                         np_vec_to_cut_vec(3 * v),
		                         np_vec_to_cut_vec(4 * v)])
		assert cmd._compile_cut_value() == expected_val


class TestPointCmd(object):
	p1 = np.array([1., 1., 1.])
	p2 = [2., 3., 4.]
	p3 = np.array([-1., -2., -3.])
	p4 = np.array([100., 1000., -10000.])
	arg_list1 = [p3]
	arg_list2 = [p2, p2]
	arg_list3 = [p1, p2, p3]
	arg_list4 = [p4, p2, p3, p4]

	def test_init(self):
		init_arg_options = [self.arg_list1, self.arg_list2,
		                    self.arg_list3, self.arg_list4]
		for args in init_arg_options:
			cmd = PointCmd(args)
			assert np.array_equal(cmd.start_pt, args[0])
			assert cmd.end_pt is None
			assert cmd.start_dir is None
			assert cmd.end_dir is None

	def test_get_cut(self):
		cmd = PointCmd(self.arg_list1)
		expected_val = 'point < -1.0000, -2.0000, -3.0000 >'
		assert cmd.get_cut() == expected_val


class TestOrientCmd(object):
	p1 = np.array([1., 1., 1.])
	p2 = [2., 3., 4.]
	p3 = np.array([-1., -2., -3.])
	p4 = np.array([100., 1000., -10000.])
	arg_list1 = [p3]
	arg_list2 = [p2, p2]
	arg_list3 = [p1, p2, p3]
	arg_list4 = [p4, p2, p3, p4]

	def test_init(self):
		init_arg_options = [self.arg_list1, self.arg_list2,
		                    self.arg_list3, self.arg_list4]
		for args in init_arg_options:
			cmd = OrientCmd(args)
			assert np.array_equal(cmd.start_dir, args[0])
			assert cmd.end_dir is None
			assert cmd.start_pt is None
			assert cmd.end_pt is None

	def test_get_cut(self):
		cmd = OrientCmd(self.arg_list1)
		expected_val = 'orient < -1.0000, -2.0000, -3.0000 >'
		assert cmd.get_cut() == expected_val


class TestOrient5XCmd(object):
	p1 = np.array([1., 1., 1.])
	p2 = [2., 3., 4.]
	p3 = np.array([-1., -2., -3.])
	p4 = np.array([100., 1000., -10000.])
	arg_list1 = [p3, p1]
	arg_list2 = [p3, p2]
	arg_list3 = [p1, p3, p3]
	arg_list4 = [p4, p4, p3, p4]

	def test_init(self):
		init_arg_options = [self.arg_list1, self.arg_list2,
		                    self.arg_list3, self.arg_list4]
		for args in init_arg_options:
			cmd = Orient5XCmd(args)
			assert np.array_equal(cmd.start_dir, args[0])
			assert np.array_equal(cmd.end_dir, args[1])
			assert cmd.start_pt is None
			assert cmd.end_pt is None

	def test_get_cut(self):
		cmd = Orient5XCmd(self.arg_list2)
		expected_val = 'orient5b < -1.0000, -2.0000, -3.0000 >' \
		               ' < 2.0000, 3.0000, 4.0000 >'
		assert cmd.get_cut() == expected_val


class TestLineCmd(object):
	p1 = np.array([1., 1., 1.])
	p2 = [2., 3., 4.]
	p3 = np.array([-1., -2., -3.])
	p4 = np.array([100., 1000., -10000.])
	arg_list1 = [p3, p1]
	arg_list2 = [p3, p2]
	arg_list3 = [p1, p3, p3]
	arg_list4 = [p4, p4, p3, p4]

	def test_init(self):
		init_arg_options = [self.arg_list1, self.arg_list2,
		                    self.arg_list3, self.arg_list4]
		for args in init_arg_options:
			cmd = LineCmd(args)
			assert np.array_equal(cmd.start_pt, args[0])
			assert np.array_equal(cmd.end_pt, args[1])
			assert cmd.start_dir is None
			assert cmd.end_dir is None

	def test_get_cut(self):
		cmd = LineCmd(self.arg_list2)
		expected_val = 'line < -1.0000, -2.0000, -3.0000 >' \
		               ' < 2.0000, 3.0000, 4.0000 >'
		assert cmd.get_cut() == expected_val


class TestLine5XCmd(object):
	p1 = np.array([1., 1., 1.])
	p2 = [2., 3., 4.]
	p3 = np.array([-1., -2., -3.])
	p4 = np.array([100., 1000., -10000.])
	arg_list1 = [p1, p2, p3, p4]

	def test_init(self):
		init_arg_options = [self.arg_list1]
		for args in init_arg_options:
			cmd = Line5XCmd(args)
			assert np.array_equal(cmd.start_pt, args[0])
			assert np.array_equal(cmd.end_pt, args[1])
			assert np.array_equal(cmd.start_dir, args[2])
			assert np.array_equal(cmd.end_dir, args[3])

	def test_get_cut(self):
		cmd = Line5XCmd(self.arg_list1)
		expected_val = 'line5b < 1.0000, 1.0000, 1.0000 >' \
		               ' < 2.0000, 3.0000, 4.0000 >' \
		               ' < -1.0000, -2.0000, -3.0000 >' \
		               ' < 100.0000, 1000.0000, -10000.0000 >'
		assert cmd.get_cut() == expected_val


"""Info Commands Tests"""


class TestInfoCmd(object):

	def test_init(self):
		cmd = InfoCmd()
		assert cmd.is_info_cmd
		assert not cmd.is_move_cmd


class TestHeaderCmd(object):
	filename1 = 'filename1'
	filename2 = 'filename2'
	info1 = 'this part usually contains date/time stamp'
	info2 = 'this part usually contains date/time stamp. Different from info1.'
	h1 = [filename1 + ' ' + info1]
	h2 = [filename1 + ' ' + info1]
	h3 = [filename1 + ' ' + info2]
	h4 = [filename2 + ' ' + info1]
	h5 = [filename2 + ' ' + info2]

	def test_init(self):
		cmd = HeaderCmd(self.h1)
		assert cmd.file_name == self.filename1
		assert cmd.info == self.info1.split()

	def test_equality_and_inequality(self):
		cmd1 = HeaderCmd(self.h1)
		cmd2 = HeaderCmd(self.h2)
		cmd3 = HeaderCmd(self.h3)
		cmd4 = HeaderCmd(self.h4)
		cmd5 = HeaderCmd(self.h5)
		assert cmd1 == cmd2
		assert not cmd1 == cmd3
		assert not cmd1 == cmd4
		assert not cmd1 == cmd5
		assert cmd1 != cmd3
		assert cmd1 != cmd4
		assert cmd1 != cmd5

	def test_get_cut(self):
		cmd = HeaderCmd(self.h1)
		expected_val = 'header %s' % self.h1[0]
		assert cmd.get_cut() == expected_val


@pytest.mark.xfail
class TestHeaderExtCmd(object):

	def test_init(self):
		assert 0

	def test_equality_and_inequality(self):
		assert 0

	def test_get_cut(self):
		assert 0


class TestCheckpointCmd(object):
	name1, name2, name3 = 'chk_pt1', 'chk_pt2', 'chk_pt3'
	recov_pt1, recov_pt2, recov_pt3 = np.array([1., 2., 3.]), \
	                                  np.array([1., 2., 3.00005]), \
	                                  np.array([-1., -2., -3.])
	per_comp1, per_comp2, per_comp3 = .1, .1, .2
	chk_pt1 = [name1, recov_pt1, per_comp1]
	chk_pt2 = [name2, recov_pt2, per_comp2]
	chk_pt3 = [name3, recov_pt3, per_comp3]
	chk_pt4 = [name1, recov_pt1, per_comp1]
	chk_pt5 = [name1, recov_pt1, per_comp2]

	def test_init(self):
		cmd = CheckpointCmd(self.chk_pt1)
		assert cmd.name == self.name1
		assert np.array_equal(cmd.recovery_pt, self.recov_pt1)
		assert cmd.per_comp == self.per_comp1

	def test_equality_and_inequality(self):
		cmd1 = CheckpointCmd(self.chk_pt1)
		cmd2 = CheckpointCmd(self.chk_pt2)
		cmd3 = CheckpointCmd(self.chk_pt3)
		cmd4 = CheckpointCmd(self.chk_pt4)
		cmd5 = CheckpointCmd(self.chk_pt5)
		assert cmd1 == cmd1
		assert cmd1 == cmd4
		assert not cmd1 == cmd2  # these only differ by name
		assert not cmd1 == cmd3
		assert cmd1 == cmd1
		assert cmd1 == cmd4
		assert cmd1 != cmd2
		assert cmd1 != cmd3
		assert cmd1 == cmd5  # this tests the default tolerance (1e-4)

	def test_get_cut(self):
		cmd1 = CheckpointCmd(self.chk_pt1)
		cmd2 = CheckpointCmd(self.chk_pt5)
		expectec_val1 = 'checkpoint %s %s %s' % (self.chk_pt1[0],
		                                         np_vec_to_cut_vec(self.chk_pt1[1]),
		                                         float_to_cut_string(self.chk_pt1[2]))
		expectec_val2 = 'checkpoint %s %s %s' % (self.chk_pt5[0],
		                                         np_vec_to_cut_vec(self.chk_pt5[1]),
		                                         float_to_cut_string(self.chk_pt5[2]))
		assert cmd1.get_cut() == expectec_val1
		assert cmd2.get_cut() == expectec_val2
		assert cmd2.get_cut() == expectec_val1  # this tests the tolerance


class TestCutterCmd(object):
	pn1, pn2, pn3, pn4 = ['106428'], ['106428'], ['105734'], ['NOT A VALID CUTTER']
	c1, c2 = CUTTERS[pn1[0]], CUTTERS[pn3[0]]

	def test_init(self):
		cmd = CutterCmd(self.pn1)
		assert cmd.cutter == self.c1
		cmd = CutterCmd(self.pn3)
		assert cmd.cutter == self.c2
		with pytest.raises(RuntimeError, message='RuntimeError Expected'):
			CutterCmd(self.pn4)  # Causes error because cutter pn is invalid

	def test_equality_and_inequality(self):
		cmd1 = CutterCmd(self.pn1)
		cmd2 = CutterCmd(self.pn2)
		cmd3 = CutterCmd(self.pn3)
		cmd5 = CutterCmd(self.pn1)
		assert cmd1 == cmd1
		assert cmd1 == cmd2
		assert cmd1 != cmd3
		assert not cmd1 != cmd1
		assert not cmd1 != cmd2
		assert not cmd1 == cmd3

	def test_get_cut(self):
		cmd = CutterCmd(self.pn1)
		expected_val = 'cutter %s %s %s %s' % (self.c1.part_number,
		                                       float_to_cut_string(self.c1.length),
		                                       float_to_cut_string(self.c1.radius),
		                                       float_to_cut_string(self.c1.height))
		assert cmd.get_cut() == expected_val

# TODO: move this for Cutter testing
# class TestCutterCmd(object):
# 	name1, name2 = '106428', '105734'
# 	len1, len2, len3, len4 = 144.094, 268.65, 144.09405, 144.0941
# 	rad1, rad2, rad3, rad4 = 3.1, 3, 3.10005, 3.1001
# 	ht1, ht2, ht3, ht4 = 5, 5.31, 5.00005, 5.0001
# 	cutter1 = [name1, len1, rad1, ht1]
# 	cutter2 = [name2, len2, rad2, ht2]
# 	cutter3 = [name1, len3, rad3, ht3]  # for testing tolerances
# 	cutter4 = [name1, len4, rad4, ht4]  # for testing tolerances
#
# 	def test_init(self):
# 		cmd = CutterCmd(self.cutter1)
# 		assert cmd.name == self.name1
# 		assert cmd.length == self.len1
# 		assert cmd.radius == self.rad1
# 		assert cmd.height == self.ht1
#
# 	def test_equality_and_inequality(self):
# 		cmd1 = CutterCmd(self.cutter1)
# 		cmd2 = CutterCmd(self.cutter2)
# 		cmd3 = CutterCmd(self.cutter3)
# 		cmd4 = CutterCmd(self.cutter4)
# 		cmd5 = CutterCmd(self.cutter1)
# 		cmd5._cmp_tol = 1e-5
# 		assert cmd1 == cmd1
# 		assert not cmd1 == cmd2
# 		assert cmd1 == cmd3  # tolerance test
# 		assert not cmd1 == cmd4  # tolerance test
# 		assert not cmd5 == cmd4  # tolerance = 1e-5
#
# 		assert not cmd1 != cmd1
# 		assert cmd1 != cmd2
# 		assert not cmd1 != cmd3  # tolerance test
# 		assert cmd1 != cmd4  # tolerance test
# 		assert cmd5 != cmd4  # tolerance = 1e-5
#
# 	def test_get_cut(self):
# 		cmd = CutterCmd(self.cutter1)
# 		expected_val = 'cutter %s %s %s %s' % (self.cutter1[0],
# 		                                       float_to_cut_string(self.cutter1[1]),
# 		                                       float_to_cut_string(self.cutter1[2]),
# 		                                       float_to_cut_string(self.cutter1[3]))
# 		assert cmd.get_cut() == expected_val


class TestPhaseCmd(object):
	phase1, phase2, phase3 = ['phase1'], ['phase2'], ['phase1']

	def test_init(self):
		cmd = PhaseCmd(self.phase1)
		assert cmd.name == self.phase1[0]

	def test_equality_and_inequality(self):
		cmd1 = PhaseCmd(self.phase1)
		cmd2 = PhaseCmd(self.phase2)
		cmd3 = PhaseCmd(self.phase3)
		assert cmd1 == cmd1
		assert not cmd1 == cmd2
		assert cmd1 == cmd3
		assert not cmd1 != cmd1
		assert cmd1 != cmd2
		assert not cmd1 != cmd3

	def test_get_cut(self):
		cmd = PhaseCmd(self.phase1)
		expected_val = 'phase %s' % self.phase1[0]
		assert cmd.get_cut() == expected_val


class TestStartshapeCmd(object):
	shape1, shape2, shape3, shape4, shape5 = ['shape1', 1], ['shape2', 2], \
	                                         ['shape1', 1], ['shape1', 2], \
	                                         ['shape2', 1]

	def test_init(self):
		cmd = StartshapeCmd(self.shape1)
		assert cmd.name == self.shape1[0]
		assert cmd.num_moves == self.shape1[1]

	def test_equality_and_inequality(self):
		cmd1 = StartshapeCmd(self.shape1)
		cmd2 = StartshapeCmd(self.shape2)
		cmd3 = StartshapeCmd(self.shape3)
		cmd4 = StartshapeCmd(self.shape4)
		cmd5 = StartshapeCmd(self.shape5)
		assert cmd1 == cmd1
		assert not cmd1 == cmd2
		assert cmd1 == cmd3
		assert not cmd1 == cmd4
		assert not cmd1 == cmd5
		assert not cmd1 != cmd1
		assert cmd1 != cmd2
		assert not cmd1 != cmd3
		assert cmd1 != cmd4
		assert cmd1 != cmd5

	def test_get_cut(self):
		cmd = StartshapeCmd(self.shape1)
		expected_val = 'startshape %s %s' % tuple(self.shape1)
		assert cmd.get_cut() == expected_val


class TestEndshapeCmd(object):
	shape1, shape2, shape3, shape4, shape5 = ['shape1', 1], ['shape2', 2], \
	                                         ['shape1', 1], ['shape1', 2], \
	                                         ['shape2', 1]

	def test_init(self):
		cmd = EndshapeCmd(self.shape1)
		assert cmd.name == self.shape1[0]
		assert cmd.num_moves == self.shape1[1]

	def test_equality_and_inequality(self):
		cmd1 = EndshapeCmd(self.shape1)
		cmd2 = EndshapeCmd(self.shape2)
		cmd3 = EndshapeCmd(self.shape3)
		cmd4 = EndshapeCmd(self.shape4)
		cmd5 = EndshapeCmd(self.shape5)
		assert cmd1 == cmd1
		assert not cmd1 == cmd2
		assert cmd1 == cmd3
		assert not cmd1 == cmd4
		assert not cmd1 == cmd5
		assert not cmd1 != cmd1
		assert cmd1 != cmd2
		assert not cmd1 != cmd3
		assert cmd1 != cmd4
		assert cmd1 != cmd5

	def test_get_cut(self):
		cmd = EndshapeCmd(self.shape1)
		expected_val = 'endshape %s %s' % tuple(self.shape1)
		assert cmd.get_cut() == expected_val


class TestDecelOnCmd(object):

	def test_init(self):
		cmd = DecelOnCmd()
		assert cmd._arg_list == []

	def test_equality_and_inequality(self):
		cmd1 = DecelOnCmd()
		cmd2 = DecelOnCmd()
		cmd3 = DecelOffCmd()
		assert cmd1 == cmd2
		assert not cmd1 == cmd3
		assert not cmd1 != cmd2
		assert cmd1 != cmd3

	def test_get_cut(self):
		cmd = DecelOnCmd()
		expected_val = 'decel_on'
		assert cmd.get_cut() == expected_val


class TestDecelOffCmd(object):

	def test_init(self):
		cmd = DecelOffCmd()
		assert cmd._arg_list == []

	def test_equality_and_inequality(self):
		cmd1 = DecelOffCmd()
		cmd2 = DecelOffCmd()
		cmd3 = DecelOnCmd()
		assert cmd1 == cmd2
		assert not cmd1 == cmd3
		assert not cmd1 != cmd2
		assert cmd1 != cmd3

	def test_get_cut(self):
		cmd = DecelOffCmd()
		expected_val = 'decel_off'
		assert cmd.get_cut() == expected_val


class TestSpeedCmd(object):
	spd1, spd2, spd3, spd4, spd5, spd6, spd7 = [1.], [2.], [1], [1.0001], \
	                                           [1.00005], [1.00004], [1.00015]

	def test_init(self):
		for spd in [self.spd1, self.spd2, self.spd3, self.spd4, self.spd5, self.spd6, self.spd7]:
			cmd = SpeedCmd(spd)
			assert cmd.speed == spd[0]

	def test_equality_and_inequality(self):
		cmd1 = SpeedCmd(self.spd1)
		cmd2 = SpeedCmd(self.spd2)
		cmd3 = SpeedCmd(self.spd3)
		cmd4 = SpeedCmd(self.spd4)
		cmd5 = SpeedCmd(self.spd5)
		cmd6 = SpeedCmd(self.spd6)
		cmd7 = SpeedCmd(self.spd7)
		assert cmd1 == cmd1
		assert cmd1 == cmd3
		assert cmd1 == cmd5
		assert cmd1 == cmd6
		assert cmd4 == cmd7
		assert not cmd1 == cmd2
		# TODO: assert not cmd1 == cmd4  # weird cmp_flt edge case
		assert not cmd1 == cmd7

		assert not cmd1 != cmd1
		assert not cmd1 != cmd3
		assert not cmd1 != cmd5
		assert not cmd1 != cmd6
		assert not cmd4 != cmd7
		assert cmd1 != cmd2
		# assert cmd1 != cmd4
		assert cmd1 != cmd7

	def test_get_cut(self):
		cmd1 = SpeedCmd(self.spd1)
		expected_val1 = 'speed %s' % float_to_cut_string(self.spd1[0])
		cmd2 = SpeedCmd(self.spd3)
		expected_val2 = 'speed %s' % float_to_cut_string(self.spd3[0])
		cmd3 = SpeedCmd(self.spd4)
		expected_val3 = 'speed %s' % float_to_cut_string(self.spd4[0])
		cmd4 = SpeedCmd(self.spd7)
		expected_val4 = 'speed %s' % float_to_cut_string(self.spd7[0])
		assert cmd1.get_cut() == expected_val1
		assert cmd2.get_cut() == expected_val2
		assert cmd3.get_cut() == expected_val3
		assert cmd4.get_cut() == expected_val4
		assert cmd1.get_cut() == cmd2.get_cut()
		assert cmd3.get_cut() != cmd4.get_cut()


class TestAccelCmd(object):
	a1, a2, a3, a4 = 1, 1., 1.0002, 1.00015
	d1, d2, d3, d4 = 1, 1., 1.0002, 1.00015
	accel1, accel2, accel3, accel4 = [a1, d1], [a2, d2], [a3, d3], [a4, d4]

	def test_init(self):
		cmd = AccelCmd(self.accel2)
		assert cmd.accel == self.accel2[0]
		assert cmd.decel == self.accel2[1]

	def test_equality_and_inequality(self):
		cmd1 = AccelCmd(self.accel1)
		cmd2 = AccelCmd(self.accel2)
		cmd3 = AccelCmd(self.accel3)
		cmd4 = AccelCmd(self.accel4)
		assert cmd1 == cmd1
		assert cmd1 == cmd2
		assert cmd3 == cmd4
		assert not cmd1 == cmd3
		assert not cmd1 == cmd4
		assert not cmd1 != cmd1
		assert not cmd1 != cmd2
		assert not cmd3 != cmd4
		assert cmd1 != cmd3
		assert cmd1 != cmd4

	def test_get_cut(self):
		cmd1 = AccelCmd(self.accel1)
		expected_val1 = 'accel %s %s' % (float_to_cut_string(self.accel1[0]),
		                                 float_to_cut_string(self.accel1[1]))
		cmd2 = AccelCmd(self.accel2)
		expected_val2 = 'accel %s %s' % (float_to_cut_string(self.accel2[0]),
		                                 float_to_cut_string(self.accel2[1]))
		assert cmd1.get_cut() == expected_val1
		assert cmd2.get_cut() == expected_val2
		assert cmd1.get_cut() == cmd2.get_cut()


class TestCutterOnCmd(object):

	def test_init(self):
		cmd = CutterOnCmd()
		assert cmd._arg_list == []

	def test_equality_and_inequality(self):
		cmd1 = CutterOnCmd()
		cmd2 = CutterOnCmd()
		cmd3 = CutterOffCmd()
		assert cmd1 == cmd2
		assert not cmd1 == cmd3
		assert not cmd1 != cmd2
		assert cmd1 != cmd3

	def test_get_cut(self):
		cmd = CutterOnCmd()
		expected_val = 'cutter_on'
		assert cmd.get_cut() == expected_val


class TestCutterOffCmd(object):

	def test_init(self):
		cmd = CutterOnCmd()
		assert cmd._arg_list == []

	def test_equality_and_inequality(self):
		cmd1 = CutterOnCmd()
		cmd2 = CutterOnCmd()
		cmd3 = CutterOffCmd()
		assert cmd1 == cmd2
		assert not cmd1 == cmd3
		assert not cmd1 != cmd2
		assert cmd1 != cmd3

	def test_get_cut(self):
		cmd = CutterOnCmd()
		expected_val = 'cutter_on'
		assert cmd.get_cut() == expected_val


class TestFCparmsCmd(object):
	n1, n2, n3 = 1., 2., 1.00005
	maxs1, maxs2, maxs3 = 1., 2., 1.00005
	mins1, mins2, mins3 = 1., 2., 1.00005
	maxf1, maxf2, maxf3 = 1., 2., 1.00005
	fc1 = [n1, maxs1, mins1, maxf1]
	fc2 = [n2, maxs2, mins2, maxf2]
	fc3 = [n3, maxs3, mins3, maxf3]

	def test_init(self):
		cmd = FCparmsCmd(self.fc1)
		assert cmd.nominal_speed == self.fc1[0]
		assert cmd.max_speed == self.fc1[1]
		assert cmd.min_speed == self.fc1[2]
		assert cmd.max_force == self.fc1[3]

	def test_equality_and_inequality(self):
		cmd1 = FCparmsCmd(self.fc1)
		cmd2 = FCparmsCmd(self.fc2)
		cmd3 = FCparmsCmd(self.fc3)
		assert cmd1 == cmd1
		assert cmd1 == cmd3
		assert not cmd1 == cmd2
		assert not cmd1 != cmd1
		assert not cmd1 != cmd3
		assert cmd1 != cmd2

	def test_get_cut(self):
		cmd = FCparmsCmd(self.fc1)
		expected_val = 'fcparms %s %s %s %s' % (float_to_cut_string(self.fc1[0]),
		                                        float_to_cut_string(self.fc1[1]),
		                                        float_to_cut_string(self.fc1[2]),
		                                        float_to_cut_string(self.fc1[3]))
		assert cmd.get_cut() == expected_val


@pytest.mark.xfail
class TestVersionCmd(object):

	def test_init(self):
		assert 0

	def test_equality_and_inequality(self):
		assert 0

	def test_get_cut(self):
		assert 0


class TestCommentCmd(object):
	m1, m2 = 'comment 1', 'comment 2'
	c1, c2, c3 = [m1], [m2], [m1]

	def test_init(self):
		cmd = CommentCmd(self.c1)
		assert cmd.text == self.c1[0]

	def test_equality_and_inequality(self):
		cmd1 = CommentCmd(self.c1)
		cmd2 = CommentCmd(self.c2)
		cmd3 = CommentCmd(self.c3)
		assert cmd1 == cmd1
		assert cmd1 == cmd3
		assert not cmd1 == cmd2
		assert not cmd1 != cmd1
		assert not cmd1 != cmd3
		assert cmd1 != cmd2

	def test_get_cut(self):
		cmd = CommentCmd(self.c1)
		expected_val = 'comment %s' % self.c1[0]
		assert cmd.get_cut() == expected_val


@pytest.mark.xfail
class TestCheckSumCmd(object):

	def test_init(self):
		assert 0

	def test_equality_and_inequality(self):
		assert 0

	def test_get_cut(self):
		assert 0









