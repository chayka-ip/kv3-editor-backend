from parser_kv3.data_classes import CommentKV3
from parser_kv3.parser_data import DataType, line_comment_start, multi_line_comment_start, multi_line_comment_end
from parser_kv3.serializers.value_serializer import is_line_valid_line_comment, is_line_valid_multi_line_comment


def serialize_comment_by_type(line: str, comment_type: str):
    if comment_type == DataType.comment_inline:
        return serialize_line_comment(line)
    if comment_type == DataType.comment_multi:
        return serialize_multi_line_comment(line)


def serialize_line_comment(line: str):
    line = line.strip()
    if is_line_valid_line_comment(line):
        value = clean_up_comment(line, is_inline=True)
        return CommentKV3(value=value, comment_type=DataType.comment_inline)


def serialize_multi_line_comment(line: str):
    line = line.strip()
    if is_line_valid_multi_line_comment(line):
        value = clean_up_comment(line, is_inline=False)
        return CommentKV3(value=value, comment_type=DataType.comment_multi)


def clean_up_comment(line: str, is_inline: bool):
    if is_inline:
        return line.lstrip(line_comment_start).strip()
    return line.lstrip(multi_line_comment_start).rstrip(multi_line_comment_end).strip()
