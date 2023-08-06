from .lycanthropy import (snake_to_camel, SnakeToCamel, snakeToCamel,
                          camel_to_snake, CamelToSnake, camelToSnake,
                          snake_to_pascal, SnakeToPascal, snakeToPascal,
                          morph_dict)

__all__ = [
    'snake_to_camel',
    'SnakeToCamel',
    'snakeToCamel',
    'snake_to_pascal',
    'SnakeToPascal',
    'snakeToPascal',
    'camel_to_snake',
    'CamelToSnake',
    'camelToSnake',
    'morph_dict',
]
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
