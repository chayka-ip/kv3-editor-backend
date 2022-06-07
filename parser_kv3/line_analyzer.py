from parser_kv3.parser_data import *
from parser_kv3.string_entity_checker import StringEntityChecker
from parser_kv3.serializers.value_serializer import is_valid_property_value_with_string_flag, get_value_type


def get_data_structure_scope_flags_from_line(line: str):
    line = line.strip().rstrip(',')

    if is_inline_array(line) or is_inline_object(line):
        return None

    for open_seq in data_structure_open_seq:
        if line.startswith(open_seq):
            return open_seq

    for close_seq in data_structure_close_seq:
        if line.endswith(close_seq):
            if not line_contains_inline_comment(line):
                return close_seq


def is_inline_array(line: str):
    return get_value_type(line) == DataType.array


def is_inline_object(line: str):
    return get_value_type(line) == DataType.object


def is_array_line_valid_region(line: str):
    """
        Line is valid region when:
            1. it is valid value of some type without name assigned (may end up with comma)
            2. proper comment
            3. value and comment nearby (which is bad)
     """
    has_line_comment = line_comment_start in line
    multi_line_comment_check = StringEntityChecker(line, multi_line_comment_start, multi_line_comment_end)

    no_comment_symbols = (not has_line_comment) and multi_line_comment_check.no_sequences

    if no_comment_symbols:
        return is_array_line_valid_region_no_comment(line)

    return is_array_line_valid_region_with_comment(line)


def get_array_inline_entry_value(line: str):
    return line.strip().strip(',')


def is_array_line_valid_region_no_comment(line: str):
    line = get_array_inline_entry_value(line)
    data_type = get_value_type(line)
    return True if data_type else False


def is_array_line_valid_region_with_comment(line: str):
    pass

    line = line.strip()

    has_line_comment = line_comment_start in line
    multi_line_comment_check = StringEntityChecker(line, multi_line_comment_start, multi_line_comment_end)

    has_line_comment_only = has_line_comment and multi_line_comment_check.no_sequences
    has_multi_line_comment_only = not has_line_comment and multi_line_comment_check.has_valid_entity

    is_line_comment_itself = line.startswith(line_comment_start)
    is_multiline_comment_itself = has_multi_line_comment_only and line.startswith(multi_line_comment_start)
    is_valid_comment_itself = is_line_comment_itself or is_multiline_comment_itself

    if is_valid_comment_itself:
        return True

    if has_line_comment_only:
        return is_array_line_valid_region_with_line_comment_only(line)

    if has_multi_line_comment_only:
        return is_array_line_valid_region_with_multi_line_comment_only(line)


def is_array_line_valid_region_with_line_comment_only(line: str):
    data = line.split(line_comment_start)
    potential_value = data[0].strip()
    return True if potential_value else False


def is_array_line_valid_region_with_multi_line_comment_only(line: str):
    raise NotImplementedError


def is_object_line_valid_region(line: str):
    """
        Line is valid region when:
            1. it is property with fully assigned value
            2. proper comment
            3. property with value and comment nearby (which is bad)
     """
    has_line_comment = line_comment_start in line
    multi_line_comment_check = StringEntityChecker(line, multi_line_comment_start, multi_line_comment_end)

    no_comment_symbols = (not has_line_comment) and multi_line_comment_check.no_sequences

    if no_comment_symbols:
        return is_object_line_valid_region_no_comment(line)

    return is_object_line_valid_region_with_comment(line)


def inline_property_no_comment_get_name_and_value(line: str):
    has_assignment = assignment in line
    if has_assignment:
        data = line.split(assignment)
        property_name = data[0].strip()
        property_value = data[1].strip()
        if property_name and property_value:
            if is_valid_property_value(property_value):
                return property_name, property_value


def is_object_line_valid_region_no_comment(line: str):
    return inline_property_no_comment_get_name_and_value(line)


def line_opens_multiline_segment(line: str):
    line = line.strip()
    if is_object_line_valid_region(line):
        return False

    has_assignment = assignment in line
    has_array_open = array_start in line
    has_object_open = object_start in line
    has_multi_line_comment_start = multi_line_comment_start
    has_multi_line_string_seq = multi_line_string_quotes in line

    if has_assignment:
        data = line.split(assignment)
        property_name = data[0].strip()
        property_value = data[1].strip()
        if property_name and property_value == '':
            return True

    return has_array_open or has_object_open or has_multi_line_comment_start or has_multi_line_string_seq


def line_closes_multiline_segment(line: str):
    line = line.strip()

    if line_contains_inline_comment(line):
        return False

    if is_object_line_valid_region(line):
        return False

    for ii in [multi_line_comment_end, multi_line_string_quotes]:
        if line.endswith(ii):
            return True

    for ii in [array_end, object_end]:
        if line.startswith(ii) and len(line) < 3:
            if line == ii or line.endswith(','):
                return True


def is_valid_property_value(s: str):
    array_check = StringEntityChecker(s, array_start, array_end)
    object_check = StringEntityChecker(s, object_start, object_end)
    multi_line_string_check = StringEntityChecker(s, multi_line_string_quotes, multi_line_string_quotes)

    no_array_seq = array_check.no_sequences
    no_object_seq = object_check.no_sequences
    no_multi_line_seq = multi_line_string_check.no_sequences

    is_simple_type = no_array_seq and no_object_seq and no_multi_line_seq

    has_valid_array = array_check.has_valid_entity
    has_valid_object = object_check.has_valid_entity
    has_valid_multi_line = multi_line_string_check.has_valid_entity

    is_complex_type = has_valid_array or has_valid_object or has_valid_multi_line

    is_resource_string = is_valid_property_value_with_string_flag(s)

    return is_simple_type or is_complex_type or is_resource_string


def is_object_line_valid_region_with_comment(line: str):
    # we can check numerous variations here BUT i won't add something complex until it would be needed

    has_line_comment = line_comment_start in line
    multi_line_comment_check = StringEntityChecker(line, multi_line_comment_start, multi_line_comment_end)

    is_line_comment_only = has_line_comment and multi_line_comment_check.no_sequences
    is_multi_line_comment_only = not has_line_comment and multi_line_comment_check.has_valid_entity

    line = line.strip()

    if is_line_comment_only:
        return is_object_line_valid_region_with_line_comment_only(line)

    if is_multi_line_comment_only:
        return is_object_line_valid_region_with_multi_line_comment_only(line)


def is_object_line_valid_region_with_line_comment_only(line: str):
    if line.startswith(line_comment_start):
        return True
    comment_start_index = line.index(line_comment_start)
    data = line[:comment_start_index]
    return is_object_line_valid_region_no_comment(data)


def is_object_line_valid_region_with_multi_line_comment_only(line: str):
    if line.startswith(multi_line_comment_start):
        return True
    if line.endswith(multi_line_comment_end):
        comment_start_index = line.index(multi_line_comment_start)
        data = line[:comment_start_index]
        return is_object_line_valid_region_no_comment(data)


def line_contains_inline_comment(line: str):
    return line_comment_start in line
