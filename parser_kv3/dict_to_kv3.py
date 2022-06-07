from parser_kv3.data_keys import *
from parser_kv3.dict_to_kv3_data_modif import modify_value_list
from parser_kv3.parser_data import *
from parser_kv3.serializers.value_serializer import convert_value_to_simple_str_with_quotes

lf = '\n'
space = ' '

comment_separator = '-' * 20


def get_lf(n):
    return lf * n


def get_tab(n):
    return space * n


def json_to_kv3(data: dict):
    try:
        return dict_to_kv3_string(data)
    except:
        return "unable to convert data"


def dict_to_kv3_string(data: dict):
    result_str = ''
    header: str = data[header_key]
    root_dict: dict = data[root_key]

    if header:
        result_str += header + get_lf(1)

    assert root_dict
    root_dict.pop(name_key, None)

    value = root_dict.get(value_key, [])
    value = modify_value_list(value)
    root_dict[value_key] = value

    root_str = kv3_dict_to_str(d=root_dict, indent_lvl=0, indent_per_lvl=4)

    return result_str + root_str


def kv3_dict_to_str(d: dict, indent_lvl: int = 0, indent_per_lvl: int = 0):
    indent = get_lvl_total_indent(indent_lvl, indent_per_lvl)
    name = d.get(name_key, None)
    data_type = d.get(data_type_key, None)
    value = d.get(value_key, None)
    comments = d.get(comment_key, None)

    # primitive type is assumed

    if data_type is None:
        assert value is not None
        return plain_property_to_string(name, value, indent)

    # handle complex type

    assert isinstance(value, list)
    assert data_type in complex_types

    is_array = data_type == DataType.array
    is_object = data_type == DataType.object

    if is_array:
        assert name is not None

    result = ''

    # only object-related comments are supported  now
    if comments and is_object:
        result += comments_to_string(comments, indent) + lf

    result += get_complex_value_stringified(name, data_type, value, indent_lvl, indent_per_lvl)

    return result


def get_complex_value_stringified(name: str, data_type: str, value: list, indent_lvl: int, indent_per_lvl: int):
    is_array = data_type == DataType.array
    is_object = data_type == DataType.object

    assert is_array or is_object
    assert isinstance(value, list) and len(value) > 0

    indent = get_lvl_total_indent(indent_lvl, indent_per_lvl)

    str_list = get_value_list_items_stringified(value, indent_lvl, indent_per_lvl)
    return string_obj_list_to_string(name, str_list, indent, is_array=is_array)


def get_value_list_items_stringified(value: list, indent_lvl: int, indent_per_lvl: int):
    next_indent_lvl = indent_lvl + 1

    out_list = []

    for item in value:
        item_str = kv3_dict_to_str(item, next_indent_lvl, indent_per_lvl)
        out_list.append(item_str)

    return out_list


def string_obj_list_to_string(name: str, data: list, indent: int, is_array: bool):
    tab = get_tab(indent)

    if is_array:
        data = f',\n'.join(data)
        _open_char = array_start
        _close_char = array_end
    else:
        data = f'\n'.join(data)
        _open_char = object_start
        _close_char = object_end

    _define = ''
    if name:
        _define = tab + name + ' = ' + lf

    _open = tab + _open_char + lf
    _close = tab + _close_char

    return _define + _open + data + lf + _close


def plain_property_to_string(name: str, value: str, indent: int):
    tab = get_tab(indent)
    if isinstance(value, str):
        value = convert_value_to_simple_str_with_quotes(value)

    if name:
        return f'{tab}{name} = {value}'
    return f'{tab}{value}'


def comments_to_string(comments: list, indent: int):
    tab = get_tab(indent)
    two_line_skip = 2 * lf
    separator = two_line_skip + tab + comment_separator + two_line_skip

    _open = tab + multi_line_comment_start + two_line_skip
    _close = two_line_skip + tab + multi_line_comment_end

    formatted_comments = []
    for item in comments:
        item = item.strip()
        if isinstance(item, str):
            if item == separator:
                continue

            if lf in item:
                item = set_up_indents_for_multiline(item, indent)
            f = tab + item
            formatted_comments.append(f)

    data_str = separator.join(formatted_comments)

    return _open + data_str + _close


def set_up_indents_for_multiline(s: str, indent: int):
    tab = get_tab(indent)
    j = lf + tab
    s = s.strip().split('\n')
    s = [i.strip() for i in s]
    return j.join(s)


def get_lvl_total_indent(indent_lvl: int, indent_per_lvl: int):
    return indent_lvl * indent_per_lvl
