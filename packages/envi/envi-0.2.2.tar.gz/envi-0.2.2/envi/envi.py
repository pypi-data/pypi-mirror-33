"""Main module."""
import os
import functools

__all__ = [
    'get', 'mk_shortcut', 'get_float', 'get_int', 'get_bool', 'get_str', 'IS_OK'
]

IS_OK = ['True', ]
MISSING_VALUE = object()


def get(name, cast, required=True, default=None, validate=lambda x: None, **kwargs):
    """Get name from env.

    :param str name: The variable name
    :param callable cast: The function who cast the variable
    :param bool required: Default True
    :param any default: if `required` default is ignored
    :param callable validate: The function who validates the variable

    :return: variable
    :rtype: same as `cast` return

    :raises ValueError: if `cast` is not a callable
    :raises AttributeError: if `required` and `name` are both undefined
    """

    if not callable(cast):
        msg = 'cast: {} is not a callable'.format(
            cast.__class__.__name__
        )
        raise ValueError(msg)

    value = os.environ.get(name, MISSING_VALUE)

    if value is MISSING_VALUE:
        if required:
            raise AttributeError('{} is required'.format(name))
        validate(default)
        return default

    casted = cast(value)
    validate(casted)
    return casted


def mk_shortcut(cast):
    """ciao."""
    return functools.partial(get, cast=cast)


get_str = mk_shortcut(str)
get_str.__name__ = 'get_str'
get_str.__doc__ = """
    Get str from env.

    :param str name: The variable name
    :param kwargs: see :py:func:`get`

    :return: variable
    :rtype: str
    """

get_float = mk_shortcut(float)
get_float.__name__ = 'get_float'
get_float.__doc__ = """
    Get float from env.

    :param str name: The variable name
    :param kwargs: see :py:func:`get`

    :return: variable
    :rtype: float
    """

get_int = mk_shortcut(int)
get_int.__name__ = 'get_int'
get_int.__doc__ = """
    Get int from env.

    :param str name: The variable name
    :param kwargs: see :py:func:`get`

    :return: variable
    :rtype: int
    """


def get_bool(name, is_ok=None, **kwargs):
    """Get bool from env.

    :param str name: The variable name
    :param list(str) is_ok: truthy string list
    :param kwargs: see :py:func:`get`

    :return: variable
    :rtype: bool
    """
    if not is_ok:
        is_ok = IS_OK
    return get(name, lambda x: x in is_ok, **kwargs)
