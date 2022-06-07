from collections import namedtuple

from parser_kv3.kv3_keys import *

__DataType = namedtuple('DataType',
                        'bool int double str str_flag str_multiline array object comment_inline comment_multi')

DataType = __DataType(*__DataType._fields)

header_start = '<!--'
header_end = '-->'

assignment = '='

object_start = '{'
object_end = '}'

array_start = '['
array_end = ']'

string_quotes = '"'
multi_line_string_quotes = '"""'

b_true = 'true'
b_false = 'false'

resource_flag_regular = 'resource'
resource_flag_deferred = 'deferred_resource'

line_comment_start = '//'

multi_line_comment_start = '/*'
multi_line_comment_end = '*/'

data_structure_open_seq = [object_start, array_start]
data_structure_close_seq = [object_end, array_end]

str_types = [DataType.str_flag, DataType.str, DataType.str_multiline]
primitive_types = [DataType.bool, DataType.int, DataType.double] + str_types

complex_types = [DataType.array, DataType.object]

composite_types = [selector_key, sequencer_key, parallel_key]
child_keys = [child_key, children_key]


def get_data_structure_open_seq(close_seq: str):
    if close_seq == object_end:
        return object_start
    if close_seq == array_end:
        return array_start
