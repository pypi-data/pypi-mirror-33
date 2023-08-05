import os.path
import numpy as np
import vtk

__all__ = ['FacetBody', 'TL']


# TODO: Add documentation
# TODO: Add log info
# TODO: Most likely merge FacetBody and TL classes
class FacetBody:

	def __init__(self, name=None):
		self.name = 'FacetBody_Name_Placeholder' if name is None else name
		self.num_points, self.num_facets, self.num_edges = 0, 0, 0
		self.body = vtk.vtkPolyData()
		self.file_ext = None

	def transform(self, mtx):
		if type(mtx) is not np.ndarray:
			raise TypeError('mtx is not an numpy array!')
		if mtx.shape != (4, 4):
			raise ValueError('mtx shape is %s but should be (4,4)!' % mtx.shape())

		# Convert numpy array to vtk matrix
		vtk_mtx = vtk.vtkMatrix4x4()
		for i in range(0, 4):
			for j in range(0, 4):
				vtk_mtx.SetElement(i, j, mtx[i, j])

		transform = vtk.vtkTransform()
		transform.SetMatrix(vtk_mtx)
		tfm_flt = vtk.vtkTransformPolyDataFilter()
		tfm_flt.SetInputData(self.body)
		tfm_flt.SetTransform(transform)
		tfm_flt.Update()
		self.body = tfm_flt.GetOutput()
		return self.body


class TL(FacetBody):

	def __init__(self, name=None):
		super().__init__(name)
		self.file_ext = '.TL'

	def read(self, file_path):

		with open(file_path, 'r') as f:
			# TODO: Handle headers. Add skip header option
			# Do nothing until asterisk '*' is read-in. '*' indicates start of facet data.
			while not f.readline().startswith('*'):
				continue

			f.readline()  # Read line after asterisk. Non-important info.
			# Read the number of points and facets
			self.num_points, self.num_facets, self.num_edges = list(map(int, f.readline().strip().split()))

			# Create vertices and facets
			points = vtk.vtkPoints()
			facets = vtk.vtkCellArray()
			self.body = vtk.vtkPolyData()

			# Read points
			for i in range(self.num_points):
				points.InsertNextPoint(list(map(float, f.readline().strip().split())))

			# Read facets
			for i in range(self.num_facets):
				facet_info = list(map(int, f.readline().strip().split()))
				facets.InsertNextCell(facet_info[0])
				for v in facet_info[1:-1]:  # first elem is num vertices, last elem is color
					facets.InsertNextCell(v)

			# TODO: (Optional) read in Surface Normals
			self.body.SetPoints(points)
			del points
			self.body.SetPolys(facets)
			del facets

			self.file_ext = os.path.splitext(file_path)[1]
			return self.body

	def save(self, dest_dir, file_name=None, num_digs=6, col='3'):
		# dest_dir must exist already!

		file_name = self.name + self.file_ext if file_name is None else file_name + self.file_ext
		file_path = os.path.join(os.path.abspath(dest_dir), file_name)

		with open(file_path, 'w') as f:
			# TODO: write header
			f.write('*\n')
			f.write(file_name + '\n')
			f.write(' '.join(list(map(str, [self.num_points, self.num_facets, self.num_edges]))) + '\n')

			# Write points
			for i in range(self.num_points):
				f.write(' '.join([str(round(val, num_digs)) for val in self.body.GetPoint(i)]) + '\n')

			# Write facets
			facets = self.body.GetPolys()
			facets.InitTraversal()
			pts = vtk.vtkIdList()

			for i in range(self.num_facets):
				facets.GetNextCell(pts)
				f.write(' '.join(list(map(str, [pts.GetNumberOfIds()] +
				                  [pts.GetId(pt) for pt in range(pts.GetNumberOfIds())] + [col]))) + '\n')

			# TODO: Write facet normals (optional)

			# normals = vtk.vtkPolyDataNormals()
			# normals.ComputeCellNormalsOn()
			# normals.SetInputData(self.body)
			# # normals.Update() # this causes issues
			# facet_normals = normals.GetOutput().GetCellData().GetNormals()
			#
			# for i in range(self.num_facets):
			# 	facet_normal = facet_normals.GetTuple3(i)
			# 	f.write(str(round(facet_normal[0], 6)) + ' ' + str(round(facet_normal[1], 6)) + ' ' + str(
			# 		round(facet_normal[2], 6)) + '\n')


if __name__ == '__main__':
	tl1 = os.path.abspath('n804701R.TL')
	# print(tl1)
	test_tl = TL(name='Test Tl')
	test_tl.read(tl1)
	t_mtx1 = np.array([[1., 0., 0., 10.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])
	test_tl.transform(t_mtx1)
	fname = 'n804701R_tfmd'
	dest = os.getcwd()
	print('dest:', dest)
	test_tl.save(dest, file_name=fname)