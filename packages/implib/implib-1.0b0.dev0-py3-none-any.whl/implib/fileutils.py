import os.path


def is_file(file_path, raise_err=True):
	exists = os.path.isfile(os.path.abspath(file_path))
	if not exists and raise_err:
		raise FileExistsError('File \'%s\' does not exist.' % file_path)
	else:
		return exists


def is_dir(dir_path, raise_err=True):
	exists = os.path.isdir(os.path.abspath(dir_path))
	if not exists and raise_err:
		raise IsADirectoryError('Directory \'%s\' does not exist.' % dir_path)
	else:
		return exists


def get_file_name(file_path, exclude_ext=False):
	name = os.path.basename(file_path)
	if exclude_ext:
		name = os.path.splitext(name)[0]
	return name


def get_dir(file_path):
	return os.path.normpath(os.path.dirname(file_path))


def get_ext(file_path):
	return os.path.splitext(os.path.normpath(file_path))[1]


def has_ext(file_path):
	return len(get_ext(file_path)) > 0


def get_clean_ext(file_path):
	return get_ext(file_path).lstrip('.').lower()


def check_ext(file_path, ext):
	return ext.lower().strip('.') == get_clean_ext(file_path)


def is_cut_file_name(file_path):
	return check_ext(file_path, 'CUT')


def is_cbf_file_name(file_path):
	return check_ext(file_path, 'CBF')


def is_cls_file_name(file_path):
	return check_ext(file_path, 'CLS')


def is_cut_file(file_path):
	return is_cut_file_name(file_path) or is_cbf_file_name(file_path) or is_cls_file_name(file_path)


def make_file_name(dir_path, file_name, ext, ext_upper=False):
	file_name = get_file_name(file_name, exclude_ext=True)
	ext = ext.upper() if ext_upper else ext.lower()
	if ext[0] != '.':
		ext = '.' + ext
	file_name += ext
	return os.path.normpath(os.path.join(dir_path, file_name))


def get_data_file_path(file_path):
	file_path = os.path.join('data', file_path)
	return os.path.abspath(os.path.join(os.path.dirname(__file__), file_path))



