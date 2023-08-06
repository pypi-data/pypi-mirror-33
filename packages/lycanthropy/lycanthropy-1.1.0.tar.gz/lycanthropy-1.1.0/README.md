# lycanthropy

[![codecov](https://codecov.io/gh/rojopolis/lycanthropy/branch/master/graph/badge.svg)](https://codecov.io/gh/rojopolis/lycanthropy/branch/master/graph/badge.svg)

A micro library to convert between snake_case and CamelCase

    import lycanthropy
    print lycanthropy.camel_to_snake('snakeCase')
    print lycanthropy.snake_to_camel('camel_case')
    print lycanthropy.snake_to_pascal('pascal_case')

    snake_case
    camelCase
    PascalCase

    print lycanthropy.morph_dict({'snake_key': None}, lycanthropy.snake_to_camel)

    {'snakeKey': None}