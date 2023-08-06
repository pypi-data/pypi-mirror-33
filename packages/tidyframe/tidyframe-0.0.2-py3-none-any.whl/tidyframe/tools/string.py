""" string function  """

import copy


def replace_by_dict(source_string, mapping):
    """
    replace string by dictionary

    Parameters
    ----------
    source_string : string
    mapping : dict

    Returns
    -------
    return_string : string
    """
    return_string = copy.copy(source_string)
    for key, value in mapping.items():
        return_string = return_string.replace(key, value)
    return return_string


uppercase_letters = [chr(x) for x in range(65, 91)]
uppercase_fullwidth_letters = [chr(x) for x in range(65313, 65339)]
lowercase_letters = [chr(x) for x in range(97, 123)]
lowercase_fullwidth_letters = [chr(x) for x in range(65345, 65371)]
digits = [chr(x) for x in range(48, 58)]
fullwidth_digits = [chr(x) for x in range(65296, 65306)]
ord_symbol = [
    33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61,
    62, 63, 91, 92, 93, 94, 95, 96, 123, 124, 125, 126, 40, 41, 65377, 65378,
    65379, 44, 46
]
ord_fullwidth_symbol = []
ord_fullwidth_symbol.extend(range(65281, 65296))
ord_fullwidth_symbol.extend(range(65306, 65312))
ord_fullwidth_symbol.extend(range(65339, 65345))
ord_fullwidth_symbol.extend(range(65371, 65382))
symbol = [chr(x) for x in ord_symbol]
fullwidth_symbol = [chr(x) for x in ord_fullwidth_symbol]
ord_whitespace = [
    9, 10, 11, 12, 13, 32, 133, 160, 8192, 8193, 8194, 8195, 8196, 8197, 8198,
    8199, 8200, 8201, 8202, 8232, 8233, 8239, 8287, 12288
]
whitespace = [chr(x) for x in ord_whitespace]
