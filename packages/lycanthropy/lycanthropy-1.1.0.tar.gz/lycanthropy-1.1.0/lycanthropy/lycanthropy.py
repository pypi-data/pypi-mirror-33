from __future__ import (division, absolute_import, 
                        print_function, unicode_literals)
import re
import six


def snake_to_camel(snake_str):
    '''
    Convert `snake_str` from snake_case to camelCase
    '''
    components = snake_str.split('_')
    if len(components) > 1:
        camel = (components[0].lower() +
                 ''.join(x.title() for x in components[1:]))
        return camel
    # Not snake_case
    return snake_str


SnakeToCamel = snake_to_camel
snakeToCamel = snake_to_camel


def snake_to_pascal(snake_str):
    '''
    Convert `snake_str` from snake_case to PascalCase
    '''
    components = snake_str.split('_')
    if len(components) > 1:
        camel = ''.join(x.title() for x in components)
        return camel
    # Not snake_case
    return snake_str


SnakeToPascal = snake_to_pascal
snakeToPascal = snake_to_pascal


def camel_to_snake(camel_str):
    '''
    Convert `camel_str` from camelCase to snake_case
    '''
    # Attribution: https://stackoverflow.com/a/1176023/633213
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


CamelToSnake = camel_to_snake
camelToSnake = camel_to_snake


def morph_dict(d, convert_function):
    """
    Convert a nested dictionary from one convention to another.
    Args:
        d (dict): dictionary (nested or not) to be converted.
        convert_function (func): function that takes the string in one
        convention and returns it in the other one.
    Returns:
        Dictionary with the new keys.
    """
    # Attribution: https://stackoverflow.com/a/33668421/633213
    new = {}
    for k, v in six.iteritems(d):
        new_v = v
        if isinstance(v, dict):
            new_v = morph_dict(v, convert_function)
        elif isinstance(v, list):
            new_v = list()
            for x in v:
                new_v.append(
                    morph_dict(x, convert_function)
                )
        new[convert_function(k)] = new_v
    return new
