from parser_kv3.parser_data import *
from parser_kv3.string_entity_checker import StringEntityChecker


def is_valid_property_value_with_string_flag(line: str):
    flag = line.startswith(resource_flag_regular) or line.startswith(resource_flag_deferred)
    has_colon = ':' in line
    if flag and has_colon:
        line = line.split(':')[1]
        return is_valid_inline_string_value(line)


def is_valid_inline_string_value(line: str):
    check = StringEntityChecker(line, string_quotes, string_quotes)
    return check.is_valid_entity


def is_valid_multi_line_string_value(line: str):
    check = StringEntityChecker(line, multi_line_string_quotes, multi_line_string_quotes)
    return check.is_valid_entity


# we can do checks for nested comments of both types but who cares...

def is_line_valid_line_comment(line: str):
    return line.startswith(line_comment_start)


def is_line_valid_multi_line_comment(line: str):
    check = StringEntityChecker(line, multi_line_comment_start, multi_line_comment_end)
    return check.is_valid_entity


def get_primitive_value_type_num_or_string(value):
    if isinstance(value, int):
        return DataType.int
    if isinstance(value, float):
        return DataType.double
    if is_boolean(value):
        return DataType.bool
    return DataType.str


def get_value_type(value: str):
    if is_boolean(value):
        return DataType.bool
    if is_double(value):
        return DataType.double
    if is_integer(value):
        return DataType.int
    if is_array(value):
        return DataType.array
    if is_object(value):
        return DataType.object
    if is_string_flag(value):
        return DataType.str_flag
    if is_string_multiline(value):
        return DataType.str_multiline
    if is_string(value):
        return DataType.str


def is_boolean(value: str):
    return value in [b_true, b_false]


def is_integer(value: str):
    try:
        int(value)
        return True
    except:
        pass


def is_double(value: str):
    try:
        float(value)
        return True
    except:
        pass


def is_string(value: str):
    return is_valid_inline_string_value(value)


def is_string_multiline(value: str):
    return is_valid_multi_line_string_value(value)


def is_string_flag(value: str):
    return is_valid_property_value_with_string_flag(value)


def is_array(value: str):
    start = value.startswith(array_start)
    end = value.endswith(array_end)
    return start and end


def is_object(value: str):
    start = value.startswith(object_start)
    end = value.endswith(object_end)
    return start and end


def convert_value_to_primitive_type(value: str):
    value = value.strip()
    data_type = get_value_type(value)
    assert data_type in primitive_types
    if is_boolean(value):
        return str(value)
    if is_double(value):
        return float(value)
    if is_integer(value):
        return int(value)
    if data_type in str_types:
        if data_type == DataType.str_multiline:
            return clean_up_multi_line_string(value)
        return clean_up_string(value)


def clean_up_multi_line_string(s: str):
    s = s.strip().strip(multi_line_string_quotes).strip()
    return s


def clean_up_string(s: str):
    s = s.strip().lstrip(string_quotes).rstrip(string_quotes).strip()
    return s


def convert_value_to_simple_str_with_quotes(s):
    return f'{string_quotes}{str(s).strip()}{string_quotes}'
