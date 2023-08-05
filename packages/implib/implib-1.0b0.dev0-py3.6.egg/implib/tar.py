import os.path
import tarfile

__all__ = ['extract_tar', 'extract_2level_tar']


def extract_tar(tar_path, dest_dir, show=True):
	"""Extract a .tar file to a specified destination.

	Arguments:
	tar_path -- tar file name.
	dest_dir -- desired extraction directory. Can be new directory.
	show -- if True, print status comments to terminal. if False, no status printing.
	"""

	tar_path = os.path.abspath(tar_path)
	# Check if tar_path exists
	if not os.path.isfile(tar_path):
		raise FileExistsError('tar \'%s\' does not exist!' % tar_path)

	# Check if tar_path is actually a .tar file
	if not tarfile.is_tarfile(tar_path):
		raise FileExistsError('Attempting to extract from tar but \'%s\' is not a tar!' % tar_path)

	# Create folder at dest_dir and change into it. This is where the archive gets extracted to.
	base, fname = os.path.split(tar_path)
	dest_dir = os.path.join(os.path.abspath(dest_dir), fname.split('.')[0])
	if not os.path.isdir(dest_dir):
		os.mkdir(dest_dir, mode=0o777)
	os.chdir(dest_dir)

	# Extract
	tar_obj = tarfile.open(tar_path, mode='r')
	if show:
		print('Extracting \'%s\'...' % fname)
	tar_obj.extractall()
	if show:
		print('Extracted tar \'%s\' into directory \'%s\'' % (tar_path, dest_dir))
	tar_obj.close()
	return dest_dir


def extract_2level_tar(archive_path, dest_dir, show=True):
	"""Extract a 2-level nested tar archive file to a specified destination."""

	archive_path = os.path.abspath(archive_path)
	dest_dir = os.path.abspath(dest_dir)
	extracted_archive_path = extract_tar(archive_path, dest_dir, show)
	for root, dirs, files in os.walk(dest_dir):
		for file in files:
			file_path = os.path.join(root, file)
			if tarfile.is_tarfile(file_path):
				extract_tar(file_path, extracted_archive_path, show)

