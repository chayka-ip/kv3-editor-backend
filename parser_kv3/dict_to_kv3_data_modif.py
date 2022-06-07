from parser_kv3.data_keys import *
from parser_kv3.kv3_keys import *
from parser_kv3.parser_data import composite_types, child_keys, DataType, complex_types


def modify_value_list(data_list: list):
    return modify_children_notation(data_list)


def modify_children_notation(data_list: list):
    data_list = modify_nested_for_children_notation(data_list)
    has_composite_type, num_children = find_out_composite_type_and_children(data_list)
    if num_children == 0:
        return data_list

    has_many_children = num_children > 1
    write_many_children = has_many_children or has_composite_type
    ch_key = children_key if write_many_children else child_key

    out_list = []
    for ii in data_list:
        assert isinstance(ii, dict)
        d = ii.copy()
        name = d.get(name_key, None)
        data_type = d.get(data_type_key, None)
        value = d.get(value_key, [])
        if name in child_keys:

            replace_value_list_by_obj = len(value) == 1 and not write_many_children

            if replace_value_list_by_obj:
                n_value = value[0]
                assert data_type in complex_types
                assert isinstance(n_value, dict)

                if data_type == DataType.array:
                    nn_value = n_value.get(value_key)
                    # v = nn_value[0]
                    value = nn_value
                else:
                    value = [n_value]
                    # v = n_value

                # value = [v]

                # todo: bug code.. works bad when data goes from web or from file due to differences

                # value = [n_value]
                data_type = DataType.object

            d[name_key] = ch_key
            d[value_key] = value
            d[data_type_key] = data_type
            out_list.append(d)
        else:
            out_list.append(d)

    return out_list


def modify_nested_for_children_notation(data_list: list):
    out_list = []
    for ii in data_list:
        if isinstance(ii, dict):
            v = ii.get(value_key, [])
            if isinstance(v, list):
                item_copy = ii.copy()
                item_copy[value_key] = modify_value_list(v)
                out_list.append(item_copy)
            else:
                out_list.append(ii)
    return out_list


def find_out_composite_type_and_children(data_list):
    has_composite_type = False
    num_children = 0
    for ii in data_list:
        if isinstance(ii, dict):
            name = ii.get(name_key, None)
            if name == child_key:
                num_children = 1
            elif name == children_key:
                num_children = len(ii.get(value_key, []))
            elif name == type_key:
                type_name = ii.get(value_key, '')
                if type_name in composite_types:
                    has_composite_type = True
    return has_composite_type, num_children
