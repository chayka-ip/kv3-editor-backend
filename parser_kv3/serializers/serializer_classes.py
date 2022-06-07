from parser_kv3.data_classes import ObjKV3
from parser_kv3.line_analyzer import get_array_inline_entry_value, inline_property_no_comment_get_name_and_value
from parser_kv3.parser_data import *
from parser_kv3.serializers.comment_serializer import serialize_comment_by_type
from parser_kv3.string_entity_checker import StringEntityChecker
from parser_kv3.serializers.value_serializer import is_line_valid_multi_line_comment, get_value_type, convert_value_to_primitive_type

""" Serializes single line entity inside parent object """


class InlineEntrySerializer:
    def __init__(self, line: str, is_obj:bool):
        self.line = line
        self.is_obj = is_obj

    @property
    def result(self):
        return self.serialize_entry(self.line)

    def serialize_entry(self, line: str):
        has_line_comment = line_comment_start in line
        multi_line_comment_check = StringEntityChecker(line, multi_line_comment_start, multi_line_comment_end)

        no_comment_symbols = (not has_line_comment) and multi_line_comment_check.no_sequences

        if no_comment_symbols:
            return self.serialize_entry_no_comment(line)
        return self.serialize_entry_with_comment(line)

    def serialize_entry_with_comment(self, line: str):
        has_line_comment = line_comment_start in line
        multi_line_comment_check = StringEntityChecker(line, multi_line_comment_start, multi_line_comment_end)

        is_line_comment_only = has_line_comment and multi_line_comment_check.no_sequences
        is_multi_line_comment_only = not has_line_comment and multi_line_comment_check.has_valid_entity

        line = line.strip()
        comment_type = ''
        comment_start_seq = ''

        if is_line_comment_only:
            comment_type = DataType.comment_inline
            comment_start_seq = line_comment_start

        if is_multi_line_comment_only:
            comment_type = DataType.comment_multi
            comment_start_seq = multi_line_comment_start

        if comment_type:
            comment_start_index = line.index(comment_start_seq)
            property_data = line[:comment_start_index].strip()
            comment_data = line[comment_start_index:].strip()

            comment_obj = serialize_comment_by_type(comment_data, comment_type)
            assert comment_obj

            if property_data:
                property_obj = self.serialize_entry_no_comment(property_data)
                property_obj.add_comment(comment_obj)
                return property_obj

            return comment_obj

    def get_name_and_value(self, line: str):
        if self.is_obj:
            return inline_property_no_comment_get_name_and_value(line)
        name = None
        value = get_array_inline_entry_value(line)
        return name, value

    def serialize_entry_no_comment(self, line: str):
        name, value = self.get_name_and_value(line)
        value_type = get_value_type(value)
        if value_type in primitive_types:
            value = convert_value_to_primitive_type(value)
        assert type
        return ObjKV3(name=name, value=value, data_type=value_type)


""" Serializes multi-line entity inside parent object """


class MultilineEntrySerializer:
    complex_type = (DataType.array, DataType.object)

    def __init__(self, lines: list, recursive_serializer):
        self.lines = lines
        self.recursive_serializer = recursive_serializer

    @property
    def result(self):
        return self.serialize_entry()

    def serialize_entry(self):
        line = '\n'.join(self.lines).strip().rstrip(',')

        is_multi_line_comment = is_line_valid_multi_line_comment(line)
        if is_multi_line_comment:
            return serialize_comment_by_type(line, DataType.comment_multi)

        # if input is valid object or array then array is being handled
        test_value_type = get_value_type(line)
        if test_value_type in self.complex_type:
            return self.serialize_array_entry(line)

        return self.serialize_object_entry(line)

    def serialize_array_entry(self, line: str):
        name = None
        data_type = get_value_type(line)
        if data_type == DataType.str_multiline:
            value = convert_value_to_primitive_type(line)
            return ObjKV3(name, value, data_type)
        if data_type in [DataType.array, DataType.object]:
            is_obj = data_type == DataType.object
            value = self.recursive_serializer(line, is_obj)
            return ObjKV3(name, value, data_type=data_type)

    def serialize_object_entry(self, line: str):
        first_assignment = line.find(assignment)
        if first_assignment >= 0:
            property_name = line[:first_assignment].strip()
            property_value = line[first_assignment + 1:].strip()

            if property_name:
                data_type = get_value_type(property_value)
                if data_type == DataType.str_multiline:
                    property_value = convert_value_to_primitive_type(property_value)
                    return ObjKV3(property_name, property_value, data_type)
                if data_type in self.complex_type:
                    is_obj = data_type == DataType.object
                    value = self.recursive_serializer(property_value, is_obj)
                    return ObjKV3(property_name, value, data_type=data_type)

