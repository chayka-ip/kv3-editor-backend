from parser_kv3.data_classes import FileKV3, ObjKV3, root_key
from parser_kv3.region_parser import RegionParser
from parser_kv3.utils import *
from parser_kv3.serializers.value_serializer import *


def kv3_file_string_to_json(s: str):
    try:
        result = serialize_from_file_string(s)
        result.simplify()
        return result.as_json()

    except:
        return {"error": "file is invalid"}


def serialize_from_file_string(s: str):
    line = read_file_line_from_string(s)
    return serialize(line)


def serialize_from_file(file_path: str):
    line = read_file_as_line(file_path)
    return serialize(line)


def serialize(line: str):
    header = read_header(line)
    if header:
        line = line.replace(header, '')
        line = line.strip()

    root = ObjKV3(name=root_key, data_type=DataType.object)
    root.value = get_serialized_object_or_array_from_line(line, is_obj=True)

    return FileKV3(header, root)


def read_header(data: str):
    header = ''
    content = data.lstrip()
    if content.startswith(header_start):
        for ii in content:
            header += ii
            if header[-3:] == header_end:
                break
    return header


def get_object_segment_from_string(line: str, trim_tips: bool):
    return get_max_string_segment_by_characters(line, object_start, object_end, trim_tips)


def get_array_segment_from_string(line: str, trim_tips: bool):
    return get_max_string_segment_by_characters(line, array_start, array_end, trim_tips)


def get_serialized_object_or_array_from_line(line: str, is_obj: bool):
    trim_tips = True
    if is_obj:
        segment = get_object_segment_from_string(line, trim_tips)
    else:
        segment = get_array_segment_from_string(line, trim_tips)

    lines = segment.split('\n')
    return RegionParser(lines, is_obj, get_serialized_object_or_array_from_line).result
