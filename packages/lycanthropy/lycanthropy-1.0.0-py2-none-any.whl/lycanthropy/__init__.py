from .lycanthropy import (snake_to_camel, SnakeToCamel, snakeToCamel,
                          camel_to_snake, CamelToSnake, camelToSnake)

__all__ = [
    'snake_to_camel',
    'SnakeToCamel',
    'snakeToCamel',
    'camel_to_snake',
    'CamelToSnake',
    'camelToSnake',
]
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
