import re


def safe_math_eval(string, unsafe_error=ValueError, locals_dict=None):
    is_unsafe = [
        any(map(
            lambda x: x in string,
            ('__', '()', '[]', '{}', 'lambda', ',', ';', ':', '"', "'")
        )),
        # Allow a-z for numpy or math functions.
        re.match(r'^[.*/+\-0-9a-zA-Z\s()_]+$', string) is None
    ]
    if any(is_unsafe):
        raise unsafe_error(f'Evaluation of {repr(string)} is considered unsafe')
    return eval(string, {'__builtins__': None}, locals_dict or {})
