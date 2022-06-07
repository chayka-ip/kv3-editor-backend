from parser_kv3.data_classes import CommentKV3, Commentable
from parser_kv3.line_analyzer import is_object_line_valid_region, is_array_line_valid_region, \
    line_opens_multiline_segment, line_closes_multiline_segment, get_data_structure_scope_flags_from_line
from parser_kv3.parser_data import get_data_structure_open_seq
from parser_kv3.serializers.serializer_classes import MultilineEntrySerializer, InlineEntrySerializer


def assign_comments_to_related_entries(serialized_objects: list):
    out_data = []
    comment_buffer = []

    for entity in serialized_objects:
        if isinstance(entity, CommentKV3):
            comment_buffer.append(entity)
            continue

        if isinstance(entity, Commentable):
            for comment in comment_buffer:
                entity.add_comment(comment)
            comment_buffer.clear()

        out_data.append(entity)

    return out_data


class NestedScopeTracker:
    def __init__(self):
        self.is_nested_scope_now = False
        self.scope_start_index: int = None
        self.scope_stack = []

    @property
    def can_exit_from_scope(self):
        return self.scope_stack == []

    def set_nested_scope(self, line_index: int):
        self.is_nested_scope_now = True
        self.scope_start_index = line_index

    def reset_nested_scope(self):
        self.is_nested_scope_now = False
        self.scope_start_index = None

    def add_scope_sequence(self, seq: str):
        if self.scope_stack:
            last_seq = self.scope_stack[-1]
            close_seq = get_data_structure_open_seq(seq)
            if close_seq == last_seq:
                self.scope_stack.pop()
                return

        self.scope_stack.append(seq)


class RegionParser:
    """
        Integral chunk of some context must provided (like object, array, etc.)
        At once there might be only one complex structure in top level - this fact make things better

    """

    def __init__(self, lines: list, is_obj: bool, recursive_serializer):
        self.lines = lines
        self.is_obj = is_obj
        self.recursive_serializer = recursive_serializer

        self.__serialized_objects = []
        self.__current_line_index = -1
        self.__scope_tracker = NestedScopeTracker()

        self.__parse()
        self.__reassign_comments()

    @property
    def result(self):
        return self.__serialized_objects

    def __reassign_comments(self):
        self.__serialized_objects = assign_comments_to_related_entries(self.__serialized_objects)

    @property
    def current_line(self) -> str:
        return self.lines[self.__current_line_index].strip()

    @property
    def current_line_is_valid_region(self):
        line = self.current_line.strip()
        if self.is_obj:
            return is_object_line_valid_region(line)
        return is_array_line_valid_region(line)

    def __serialize_current_inline_region(self):
        serialized = InlineEntrySerializer(self.current_line, self.is_obj).result
        self.__serialized_objects.append(serialized)

    def __serialize_current_multiline_region(self):
        start_index = self.__scope_tracker.scope_start_index
        end_index = self.__current_line_index + 1
        lines = self.lines[start_index: end_index]
        serialized = MultilineEntrySerializer(lines, recursive_serializer=self.recursive_serializer).result
        self.__serialized_objects.append(serialized)

    def __parse(self):
        for ll in self.lines:
            self.__current_line_index += 1
            if not ll.strip():
                continue

            self.__parser_body()

    def __parser_body(self):
        line = self.current_line
        in_nested_scope = self.__scope_tracker.is_nested_scope_now
        not_in_nested_scope = not in_nested_scope

        if self.current_line_is_valid_region and not_in_nested_scope:
            self.__serialize_current_inline_region()
            return

        scope_seq = get_data_structure_scope_flags_from_line(line)
        if scope_seq:
            self.__scope_tracker.add_scope_sequence(scope_seq)

        line_opens_multiline_data = line_opens_multiline_segment(line)
        if line_opens_multiline_data and not_in_nested_scope:
            self.__scope_tracker.set_nested_scope(self.__current_line_index)
            return

        if in_nested_scope:
            line_closes_multiline_data = line_closes_multiline_segment(line)
            can_exit_from_scope = self.__scope_tracker.can_exit_from_scope
            if line_closes_multiline_data and can_exit_from_scope:
                self.__serialize_current_multiline_region()
                self.__scope_tracker.reset_nested_scope()
                return
