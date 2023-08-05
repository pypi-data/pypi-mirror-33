import glob
import os
import shutil

from src.implib import *

__all__ = ['Case']


class Case:
	"""A class for handling cases.
	
	Key Attributes:
	
	Important Notes:
	1) ALL PATHS ARE ABSOLUTE! ALL INPUT PATHS MUST THEREFORE BE ABSOLUTE AS WELL.
	"""

	patient_file = 'patient.dat'
	tplan_file = 'tplan.dat'
	patient_key_file = 'patient.key'
	tplan_key_file = 'tplan.key'
	report_file = 'report.pdf'
	tcat_archive_ext = '*.tar.gz'

	def __init__(self, name=None, src_path=None, extracted=False):
		self.name = 'Case_Name_Placeholder' if name is None else name
		self.src_path = os.path.abspath(src_path) if src_path is not None else None
		# TODO: Check if case is well-formed if src_path provided
		self.extracted = extracted
		self.extracted_dir = self.src_path if self.extracted else None

	def extract(self, dest_dir, show=True):
		# TODO: Add fancy progress bar
		# TODO: Add flag to skip extraction of tplan.dat
		# TODO: make sure os.path.join(dest_dir, self.name) is unique when extracting
		# Setup destination directory
		dest_dir = os.path.join(os.path.abspath(dest_dir), self.name)
		if not os.path.isdir(dest_dir):
			os.mkdir(dest_dir, mode=0o777)
		print('Extracting case \'%s\' from \'%s\' into \'%s\'...' % (self.name, self.src_path, dest_dir))

		# Extract patient and tplan archives
		extract_tar(os.path.join(self.src_path, self.patient_file), dest_dir, show)
		extract_tar(os.path.join(self.src_path, self.tplan_file), dest_dir, show)

		# Copy key files and report
		if os.path.exists(os.path.join(dest_dir, self.patient_key_file)):
			os.remove(os.path.join(dest_dir, self.patient_key_file))
		shutil.copy2(os.path.join(self.src_path, self.patient_key_file), dest_dir)
		if show:
			print('Copied \'%s\' into \'%s\'.' % (self.patient_key_file, dest_dir))

		if os.path.exists(os.path.join(dest_dir, self.tplan_key_file)):
			os.remove(os.path.join(dest_dir, self.tplan_key_file))
		shutil.copy2(os.path.join(self.src_path, self.tplan_key_file), dest_dir)
		if show:
			print('Copied \'%s\' into \'%s\'.' % (self.tplan_key_file, dest_dir))

		if os.path.exists(os.path.join(dest_dir, self.report_file)):
			os.remove(os.path.join(dest_dir, self.report_file))
		shutil.copy2(os.path.join(self.src_path, self.report_file), dest_dir)
		if show:
			print('Copied \'%s\' into \'%s\'.' % (self.report_file, dest_dir))

		# Extract tcat archive if necessary
		os.chdir(self.src_path)
		tcat_archives = glob.glob(self.tcat_archive_ext)
		if len(tcat_archives) == 0:
			# No tcat archive
			pass
		elif len(tcat_archives) > 1:
			# TODO: Provide file selection prompt to choose desired archive.
			raise FileExistsError('Too many tcat archives! Please only put one tcat archive (.tar.gz) in the src directory.')
		else:
			tcat_archive = tcat_archives[0]
			extract_2level_tar(os.path.join(self.src_path, tcat_archive), dest_dir, show)
		print('Case \'%s\' extracted into \'%s\'.' % (self.name, dest_dir))

		self.extracted = True
		self.extracted_dir = dest_dir
		return dest_dir

	def align(self, dest_dir=None, name=None, show=True):
		# TODO: Add support to align CBF and SVT files
		# TODO: Speed up transform if possible
		if show:
			print('Aligning case \'%s\'...' % self.name)

		if not self.extracted:
			raise RuntimeError('Case must be extracted before aligning!')

		# Go to patient directory and get rob_gen.xml file
		patient_dir = os.path.join(self.extracted_dir, 'patient')
		os.chdir(patient_dir)
		rob_gen = os.path.join(patient_dir, glob.glob('*_rob_gen.xml')[0])

		# Setup destination directory
		name = 'Aligned_Files' if name is None else name
		base_dir = patient_dir if dest_dir is None else dest_dir
		dest_dir = os.path.join(base_dir, name)
		if not os.path.isdir(dest_dir):
			os.mkdir(dest_dir, mode=0o777)

		# Align Facet Body files to bones
		rob_gen_info = get_rob_gen_info(rob_gen)
		for comp_name, rob_file in rob_gen_info['comp_robs'].items():
			imp_files = get_rob_bone_imp_files(rob_file)
			facet_body_files = imp_files['implant_shape'] + imp_files['cavity_shape']  # At the moment, doesn't support SVT and CBF transformation
			tfm = get_xfm(rob_file)

			# Transform non-bone facet bodies
			for fb_file in facet_body_files:
				fb_name = os.path.splitext(fb_file)[0] + '_aligned'
				temp_fb = TL(fb_name)
				temp_fb.read(os.path.join(patient_dir, fb_file))
				temp_fb.transform(tfm)
				temp_fb.save(dest_dir)

			# Save bone facet body
			bone_file = os.path.join(patient_dir, get_bone_tl_file(rob_file))
			shutil.copy2(bone_file, dest_dir)

		if show:
			print('Case aligned to bone. Transformed files are located at \'%s\'.' % dest_dir)


if __name__ == '__main__':
	c1 = Case('test_case', r'X:\Individual Folders\CJG\Laptop\THINK\Projects\CaseLoader\test_cases\tka', True)
	c1.align()