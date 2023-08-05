import os.path
import xml.etree.ElementTree as ET
import numpy as np
import pprint

__all__ = ['get_rob_gen_info', 'get_bone_tl_file', 'get_rob_bone_imp_files', 'get_xfm']

# TODO: Add documentation

def get_rob_gen_info(rob_gen_file_path):
	# TODO: add abs path checking
	root = ET.parse(rob_gen_file_path).getroot()
	rob_gen_info = {'rev': None, 'case_id': None, 'side': None, 'proc_type': None, 'comp_robs': None}

	rob_gen_info['rev'] = root.attrib['revision']
	rob_gen_info['case_id'] = root.find('case_id').text
	rob_gen_info['side'] = root.find('patient').attrib['patient_side'].upper()
	rob_gen_info['proc_type'] = root.find(".//procedure_type").text.upper()
	rob_gen_info['comp_robs'] = {comp.attrib['bone']: comp.text for comp in root.findall('.//components/component')}
	return rob_gen_info


def get_rob_bone_imp_files(rob_bone_file_path, file_types=None):
	if file_types is None:
		file_types = ['cut', 'safety_volume', 'cavity_shape', 'implant_shape']
	root = ET.parse(rob_bone_file_path).getroot()
	return {ftype: [ftag.text for ftag in root.findall(".//cutting/filename[@id='" + ftype + "']")] for ftype in file_types}


def get_bone_tl_file(rob_bone_file_path):
	return ET.parse(rob_bone_file_path).getroot().find(".//surface/filename").text


def get_xfm(xml_path):
	smtx = list(map(float, ET.parse(xml_path).getroot().find(".//xfm_matrix").text.split()))
	return np.array([smtx[:4], smtx[4:8], smtx[8:], [0., 0., 0., 1.]])


if __name__ == '__main__':
	file1 = os.path.abspath(r'X:\Individual Folders\CJG\Laptop\THINK\Projects\CaseLoader\test_cases\tha\patient\ABC10008_rob_gen.xml')
	file2 = os.path.abspath(r'X:\Individual Folders\CJG\Laptop\THINK\Projects\CaseLoader\test_cases\tka\patient\CAB40008_rob_gen.xml')
	rob1 = get_rob_gen_info(file1)
	rob2 = get_rob_gen_info(file2)
	pp = pprint.PrettyPrinter()
	pp.pprint(rob1)
	pp.pprint(rob2)
	file3 = os.path.abspath(r'X:\Individual Folders\CJG\Laptop\THINK\Projects\CaseLoader\test_cases\tka\patient\CAB40008_rob_femur.xml')
	pp.pprint(get_rob_bone_imp_files(file3))
	pp.pprint(get_bone_tl_file(file3))
	pp.pprint(get_xfm(file3))