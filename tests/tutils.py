import json

from parser_kv3.serializer import serialize_from_file
from tests.data import *


def get_json_as_dict(path: str):
    with open(path) as file:
        return json.load(file)


def write_to_json(file_path: str, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def get_src_file_path(file_name: str):
    return input_samples_dir + "/" + file_name


def get_result_file_path(file_name: str, is_dict: bool, is_simplified: bool):
    name = file_name.rsplit('.')[0]
    suff = "_dict" if is_dict else "_json"
    if is_simplified:
        suff += "_simplified"
    suff += ".json"
    return output_results_dir + "/" + name + suff


def write_test_sample_output(file_name: str):
    w_file_name = file_name.rsplit('.')[0]
    src = get_src_file_path(file_name)
    result = serialize_from_file(src)
    _dict = w_file_name + "_dict.json"
    _json = w_file_name + "_json.json"
    _dict_simp = w_file_name + "_dict_simplified.json"
    _json_simp = w_file_name + "_json_simplified.json"

    write_to_json(_dict, result.as_dict())
    write_to_json(_json, result.as_json())

    result.simplify()

    write_to_json(_dict_simp, result.as_dict())
    write_to_json(_json_simp, result.as_json())


def regenerate_test_files():
    for ii in sample_file_names:
        write_test_sample_output(ii)
