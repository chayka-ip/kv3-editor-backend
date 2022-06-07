from parser_kv3.data_classes import ObjKV3, FileKV3
from parser_kv3.data_keys import *
from parser_kv3.kv3_keys import *
from parser_kv3.parser_data import complex_types
from parser_kv3.serializers.value_serializer import get_primitive_value_type_num_or_string


def collect_value_of_attr(obj: ObjKV3, attr_name: str):
    data_set = __collect_value_of_attr_recursive(obj, attr_name)
    return sorted(list(data_set))


def __collect_value_of_attr_recursive(obj: ObjKV3, attr_name: str):
    out_data = set()
    assert hasattr(obj, attr_name)
    attr_value = getattr(obj, attr_name)
    is_string = isinstance(attr_value, str)

    if obj.is_primitive_type and attr_value and is_string:
        only_numbers = __is_string_numbers_combined(attr_value)
        if not only_numbers:
            out_data.add(attr_value)

    if obj.is_complex_type:
        for ii in obj.value:
            if isinstance(ii, ObjKV3):
                nested_res = __collect_value_of_attr_recursive(ii, attr_name)
                out_data.update(nested_res)

    return out_data


def __is_string_numbers_combined(s: str):
    for ii in s.split(' '):
        v = ii.strip()
        if v:
            try:
                float(v)
            except:
                return False
    return True


def get_objects_with_nested(obj: ObjKV3):
    obj_list = []
    if obj.is_complex_type:
        for ii in obj.value:
            if isinstance(ii, ObjKV3):
                name = getattr(ii, name_key, None)
                if name in [child_key, children_key]:
                    obj_list.append(obj)
                    for nested in ii.value:
                        obj_list += get_objects_with_nested(nested)

    return obj_list


def get_sibling_props_around_children(obj_list: list):
    raw_child = []
    raw_children = []
    for ii in obj_list:
        if isinstance(ii, ObjKV3):
            is_child_type = None
            all_props = []
            v = ii.as_dict()[value_key]
            for data_dict in v:
                if isinstance(data_dict, dict):
                    name = data_dict[name_key]
                    if name == child_key:
                        is_child_type = True
                    elif name == children_key:
                        is_child_type = False

                    if name not in [child_key, children_key]:
                        name = data_dict.get(name_key, '')
                        value = data_dict.get(value_key, '')
                        all_props.append({name_key: name, value_key: value})

            assert is_child_type is not None

            if is_child_type:
                raw_child += all_props
            else:
                raw_children += all_props

    w_child = remove_duplicated_dicts(raw_child)
    w_children = remove_duplicated_dicts(raw_children)

    return {children_key: w_children, child_key: w_child}


def remove_duplicated_dicts(dict_list: list):
    out_list = []
    for ii in dict_list:
        if isinstance(ii, dict):
            if ii not in out_list:
                out_list.append(ii)
    return out_list


def get_file_object_from_dict(header: str, root_dict: dict):
    root = get_kv3_obj_from_dict(root_dict)
    file = FileKV3(header, root)
    return file


def get_kv3_obj_from_dict(d: dict):
    name = d.get(name_key, None)
    value = d.get(value_key, None)
    data_type = d.get(data_type_key, None)
    comments = d.get(comment_key, [])

    if data_type is None:
        data_type = get_primitive_value_type_num_or_string(value)

    obj = ObjKV3(name, value, data_type)
    obj.comments = comments

    if data_type in complex_types:
        v = []
        assert isinstance(value, list)
        for ii in value:
            nested_obj = get_kv3_obj_from_dict(ii)
            v.append(nested_obj)
        obj.value = v.copy()

    return obj
