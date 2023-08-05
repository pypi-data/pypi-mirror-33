from setuptools import setup, find_packages
from codecs import open
import os.path

cur_dir = os.path.abspath(os.path.dirname(__file__))

# Get long description from the README file
with open(os.path.join(cur_dir, 'README.rst'), encoding='utf-8') as f:
	long_description = f.read()

# TODO: version should come from init

setup(
	name='implib',
	version='1.0b0-dev1',
	description='Python library for the Implant Group at Think Surgical Inc.',
	long_description=long_description,
	author='C.J. Geering',
	author_email='cgeering@thinksurgical.com',
	url='http://stash/projects/IMP/repos/implibpythonpackage/browse/implib',
	license='Proprietary License, Copyright (c) 2017, Think Surgical Inc.',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'License :: Other/Proprietary License',
		'Programming Language :: Python :: 3.6',
		'Topic :: Scientific/Engineering',
		'Topic :: Scientific/Engineering :: Medical Science Apps.',
		'Topic :: Software Development :: Libraries',
	],
	keywords='implant think tsi surgical robot robotics tplan tcat tka tha',
	packages=find_packages(where='src'),
	package_dir={'': 'src'},
	install_requires=['numpy >=1.13.1'],
	python_requires='>=3.6.0',
	include_package_data=True
)

# TODO: Why is include_package_data set to True? --> because /data/ includes tool definitions
# TODO: add python_requries arg to setup()
# TODO: convert __file__ references in pkg to use pkg_resources

# install_requires = [
# 	                   'numpy >=1.13.1',
# 	                   'vtk >= 7.1.1'],