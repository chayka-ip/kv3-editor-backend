from unittest import TestCase

from tests.tutils import *


class TestOutput(TestCase):
    def setUp(self):
        self.sample_file_names = sample_file_names

    def set_data(self, file_name: str):
        src_path = get_src_file_path(file_name)
        dict_path = get_result_file_path(file_name, is_dict=True, is_simplified=False)
        json_path = get_result_file_path(file_name, is_dict=False, is_simplified=False)
        dict_simp_path = get_result_file_path(file_name, is_dict=True, is_simplified=True)
        json_simp_path = get_result_file_path(file_name, is_dict=False, is_simplified=True)

        self.result_obj = serialize_from_file(src_path)
        self.out_dict = get_json_as_dict(dict_path)
        self.out_json = get_json_as_dict(json_path)
        self.out_dict_simp = get_json_as_dict(dict_simp_path)
        self.out_json_simp = get_json_as_dict(json_simp_path)

    @property
    def as_dict(self):
        return self.result_obj.as_dict()

    @property
    def as_json(self):
        return self.result_obj.as_json()

    def test_out_dict(self):
        for file_name in self.sample_file_names:
            with self.subTest(ii=file_name):
                self.set_data(file_name)

                self.assertEqual(self.as_dict, self.out_dict)
                self.assertEqual(self.as_json, self.out_json)

                self.result_obj.simplify()

                self.assertEqual(self.as_dict, self.out_dict_simp)
                self.assertEqual(self.as_json, self.out_json_simp)
