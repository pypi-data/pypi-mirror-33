from tidyframe.tools.string import *


def test_replace_by_dict_uppdercase():
    map_uppercase_letters = {
        x: y
        for x, y in zip(uppercase_letters, uppercase_fullwidth_letters)
    }
    replace_by_dict('/'.join(uppercase_letters), map_uppercase_letters)


def test_replace_by_dict_lowercase():
    map_lowercase_letters = {
        x: y
        for x, y in zip(lowercase_letters, lowercase_fullwidth_letters)
    }
    replace_by_dict('/'.join(lowercase_letters), map_lowercase_letters)


def test_replace_by_dict_digits():
    map_digits = {x: y for x, y in zip(digits, fullwidth_digits)}
    replace_by_dict('/'.join(digits), map_digits)
