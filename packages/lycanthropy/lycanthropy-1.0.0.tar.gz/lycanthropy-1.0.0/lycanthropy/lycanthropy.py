import re


def snake_to_camel(snake_str, style='lower'):
    '''
    Convert `snake_str` from snake_case to camelCase
    `style`: 'lower'  = camelCase
             'upper'  = CamelCase
             'pascal' = CamelCase
    '''
    components = snake_str.split('_')
    if len(components) > 1:
        if style.lower() == 'upper' or style.lower() == 'pascal':
            camel = ''.join(x.title() for x in components)
        else:
            camel = (components[0].lower() +
                     ''.join(x.title() for x in components[1:]))
        return camel
    # Not snake_case
    return snake_str


SnakeToCamel = snake_to_camel
snakeToCamel = snake_to_camel


def camel_to_snake(camel_str):
    '''
    Convert `camel_str` from camelCase to snake_case
    '''
    # Attribution: https://stackoverflow.com/a/1176023/633213
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


CamelToSnake = camel_to_snake
camelToSnake = camel_to_snake
