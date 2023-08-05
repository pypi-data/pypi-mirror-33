import csv
from .fileutils import get_data_file_path

__all__ = ['Cutter', 'CUTTERS']

_cutters_file = get_data_file_path('cutters.csv')
_cutter_shapes_file = get_data_file_path('cutter_shapes.csv')


# ALL UNITS ARE EXPECTED TO BE IN MILLIMETERS
class Cutter(object):

	def __init__(self, pn, slv, drv, prb, length, rad, ht, shp, xy_stiff, z_stiff):
		self.part_number = pn
		self.sleeve = slv
		self.drive = drv
		self.probe = prb
		self.length = float(length)
		self.radius = float(rad)
		self.height = float(ht)
		self.shape = shp
		self.xy_stiffness = float(xy_stiff)
		self.z_stiffness = float(z_stiff)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			result = self.part_number == other.part_number and \
			         self.sleeve == other.sleeve and \
			         self.drive == other.drive and \
			         self.probe == other.probe and \
			         self.length == other.length and \
			         self.radius == other.radius and \
			         self.height == other.height and \
			         self.shape == other.shape and \
			         self.xy_stiffness == other.xy_stiffness and \
			         self.z_stiffness == other.z_stiffness
			return result
		return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result


def make_cutters():
	cutters = {}
	with open(_cutters_file, 'r', newline='') as csvfile:
		dict_reader = csv.DictReader(csvfile)
		for row in dict_reader:
			cutter = Cutter(row['part_number'],
			                row['sleeve'],
			                row['drive'],
			                row['probe'],
			                row['length'],
			                row['radius'],
			                row['height'],
			                row['shape'],
			                row['xy_stiffness'],
			                row['z_stiffness'])
			cutters.update({cutter.part_number: cutter})
	return cutters

CUTTERS = make_cutters()


