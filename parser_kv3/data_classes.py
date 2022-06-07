from parser_kv3.kv3_keys import *
from parser_kv3.parser_data import DataType, complex_types, str_types, primitive_types
from parser_kv3.data_keys import *


class CommentKV3:
    def __init__(self, value='', comment_type: str = DataType.comment_inline):
        self.comment_type = comment_type
        self.value = value

    def set_type(self, comment_type: str):
        self.comment_type = comment_type

    def set_value(self, value: str):
        self.value = value

    def __str__(self):
        return f'CommentKV3: {self.value}, {self.comment_type}'

    def as_dict(self):
        return {value_key: self.value, data_type_key: self.comment_type}

    def convert_to_multiline(self):
        self.comment_type = DataType.comment_multi


class Commentable:
    def __init__(self):
        self.comments = []

    def add_comment(self, comment: CommentKV3):
        self.comments.append(comment)

    def get_comments_as_dict(self):
        return {comment_key: [k.as_dict() for k in self.comments]}

    def get_comments_as_json(self):
        return {comment_key: [k.value for k in self.comments]}

    def simplify_comments(self):
        for ii in self.comments:
            if isinstance(ii, CommentKV3):
                ii.convert_to_multiline()


class ObjKV3(Commentable):
    """value is primitive string or numeric type in case of primitive data type or list of objects in complex case"""

    def __init__(self, name: str = '', value=None, data_type=None):
        super().__init__()
        self.name = name
        self.value = value
        self.data_type = data_type

    def __str__(self):
        return f'ObjKV3: name: {self.name}, value: {self.value}, type: {self.data_type}, comments: {self.comments}'

    @property
    def is_primitive_type(self):
        return self.data_type in primitive_types

    @property
    def is_complex_type(self):
        return self.data_type in complex_types

    def as_json(self):
        d = {}
        if self.name:
            d.update({name_key: self.name})

        if self.is_complex_type:
            d.update({data_type_key: self.data_type})

        d.update({value_key: self.convert_value_for_json()})

        comments = self.get_comments_as_json()
        if comments[comment_key]:
            d.update(comments)

        return d

    def convert_value_for_json(self):
        return self.convert_value_to_format('as_json')

    def as_dict(self) -> dict:
        d = {name_key: self.name, value_key: self.convert_value_for_dict(), data_type_key: self.data_type}
        d.update(self.get_comments_as_dict())
        return d

    def convert_value_for_dict(self):
        return self.convert_value_to_format('as_dict')

    def convert_value_to_format(self, method_name):
        if self.is_primitive_type:
            return self.value

        nested_data = []
        for ii in self.value:
            if isinstance(ii, ObjKV3):
                assert hasattr(ii, method_name) and callable(getattr(ii, method_name))
                data = getattr(ii, method_name)()
                nested_data.append(data)

        return nested_data

    def simplify(self):
        self.simplify_types()
        self.simplify_structure()

    def simplify_types(self):
        self.simplify_comments()
        self.simplify_primitive_type()
        self.simplify_complex_type()

    def simplify_primitive_type(self):
        if self.data_type in str_types:
            self.value = self.value.strip().replace('\n', '')
            self.data_type = DataType.str

    def simplify_complex_type(self):
        if self.is_complex_type:
            for ii in self.value:
                if isinstance(ii, ObjKV3):
                    ii.simplify_types()

    def simplify_structure(self):
        self.move_child_to_children_array()
        if self.is_complex_type:
            for ii in self.value:
                if isinstance(ii, ObjKV3):
                    ii.simplify_structure()

    def move_child_to_children_array(self):

        child_obj = self.get_object_with_name_from_value(child_key)
        children_obj = self.get_object_with_name_from_value(children_key)
        need_create_children = children_obj is None

        if child_obj:
            child_obj.name = ""
            if need_create_children:
                children_obj = ObjKV3(name=children_key, value=[], data_type=DataType.array)

            children_obj.value.append(child_obj)

            if need_create_children:
                assert isinstance(self.value, list)
                self.value.append(children_obj)

            self.value.remove(child_obj)

    def get_object_with_name_from_value(self, obj_name: str):
        if self.is_complex_type:
            for ii in self.value:
                if isinstance(ii, ObjKV3):
                    if ii.name == obj_name:
                        return ii


class FileKV3:
    def __init__(self, header='', root: ObjKV3 = None):
        self.header = header
        self.root = root

    def simplify(self):
        if self.root:
            self.root.simplify()

    def as_dict(self):
        return {header_key: self.header, root_key: self.root.as_dict()}

    def as_json(self):
        if self.root:
            return {header_key: self.header, root_key: self.root.as_json()}
