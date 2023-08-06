""" deal with dict object """

from copy import copy
from functools import reduce
from funcy import get_in


def flatten_dict(source_dict, name_delimiter='_', inner_name=False):
    """
    flatten nest dict

    Parameters
    ----------
    source_dict : nest dict
    name_delimiter : flatten name delimiter(non-use when inner_name is True)
    inner_name : False, use innermost name as retrun dict key or not 

    Returns
    -------
    flatten dict
    """
    assert isinstance(source_dict, dict), "import source_dict is not dict"
    json_name = {}
    for key in source_dict.keys():
        if isinstance(get_in(source_dict, [key]), dict):
            val = [True, [key]]
            json_name.update({key: val})
        else:
            val = [False, [key]]
            json_name.update({key: val})
    while True:
        key_inner = list(filter(lambda x: json_name.get(x)[0], json_name))
        if key_inner:
            for x in key_inner:
                dict_to_update_json_name = {}
                val = json_name.get(x)[1]
                for key in get_in(source_dict, val).keys():
                    val_in = copy(val)
                    val_in.append(key)
                    if isinstance(get_in(source_dict, val_in), dict):
                        dict_to_update = {
                            reduce(lambda x, y: x + name_delimiter + y, val_in):
                            [True, val_in]
                        }
                    else:
                        dict_to_update = {
                            reduce(lambda x, y: x + name_delimiter + y, val_in):
                            [False, val_in]
                        }
                    dict_to_update_json_name.update(dict_to_update)
                json_name.update(dict_to_update_json_name)
                json_name.pop(x)
        else:
            break
    if inner_name:
        return {
            json_name.get(x)[1][-1]: get_in(source_dict,
                                            json_name.get(x)[1])
            for x in json_name.keys()
        }
    else:
        return {
            x: get_in(source_dict,
                      json_name.get(x)[1])
            for x in json_name.keys()
        }
