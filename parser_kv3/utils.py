def read_file_line_from_string(s: str):
    lines = s.split('\r')
    return join_lines_to_string(lines)


def read_file_as_line(path: str):
    """Returns file content as line but preserving multi line  comments"""
    with open(path) as file:
        return join_lines_to_string(file.readlines())


def join_lines_to_string(lines: list):
    return ' '.join(lines)


def get_max_string_segment_by_characters(data: str, ch_start: str, ch_end: str, trim_tips: bool):
    start_index = data.find(ch_start)
    end_index_from_end = data[::-1].find(ch_end)

    has_start_index = start_index >= 0
    has_end_index = end_index_from_end >= 0
    not_found = not (has_start_index and has_end_index)

    if not_found:
        return ''

    end_index = len(data) - end_index_from_end

    if trim_tips:
        start_index += 1
        end_index -= 1

    return data[start_index: end_index]
