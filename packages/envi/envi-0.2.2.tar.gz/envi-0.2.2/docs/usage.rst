=====
Usage
=====

To use envi in a project::

    import envi

To :py:func:`envi.get` a variables from environment::

    >>> var = envi.get('VAR', str)  # VAR=test
    >>> print(var, type(var))
    test <type 'str'>

Cast
====

`cast` should be a callable::

    >>> import json
    >>> var = envi.get('VAR', json.loads)  # VAR='{"key": "value"}'
    >>> print(var, type(var))
    {'key': 'value'} <class 'dict'>

otherwise an exception will be raised::

    >>> var = envi.get('VAR', None)  # VAR=test
      File "<stdin>", line 1, in <module>
      File "/envi/envi.py", line 15, in get
        raise ValueError(msg)
    ValueError: cast: NoneType is not a callabe

Required & Default
==================

in **envi** all variables are `required`, to accept a nullable variable you must be explicit::

    >>> var = envi.get('VAR', str, required=False)
    >>> print(var, type(var))
    None <class 'NoneType'>

otherwise an exception will be raised::

    >>> var = envi.get('VAR', str)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/envi/envi.py", line 21, in get
        raise AttributeError('{} is required'.format(var))
    AttributeError: VAR is required

also you can set a `default` for nullabe variable::

    >>> var = envi.get('VAR', str, required=False, default=True)
    >>> print(var, type(var))
    True <class 'bool'>

Validation
==========

if you want more control over your variables you can also `validate` them::

    >>> def test(case):
    ...     if case['key'] == 'valuex':
    ...         return None
    ...     else:
    ...         raise ValueError('invalid')
    >>> var = envi.get('VAR', json.loads, validate=test)  # VAR='{"key": "value"}'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/simone/github/envi/envi/envi.py", line 27, in get
        validate(casted)
      File "<stdin>", line 6, in test
    ValueError: invalid

the `default` values ​​are also validated::

    >>> default={"key": "value"}
    >>> var = envi.get('VAR1', json.loads, required=False, default=default, validate=test)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/simone/github/envi/envi/envi.py", line 27, in get
        validate(casted)
      File "<stdin>", line 6, in test
    ValueError: invalid

Shortcut
========

:py:func:`envi.get_str` return variable as `str`::

    >>> var = envi.get_str('VAR')  # VAR=string
    >>> print(var, type(var))
    string <type 'str'>

:py:func:`envi.get_bool` return variable as `bool`::

    >>> var = envi.get_bool('VAR')  # VAR=True
    >>> print(var, type(var))
    True <type 'bool'>

.. note::

    :py:func:`envi.get_bool` check if variable literally match 'True', to extend use `is_ok` argument::

        var = envi.get_bool('VAR', is_ok=['True', 'yes', '1'])

:py:func:`envi.get_int` return variable as `int`::

    >>> var = envi.get_int('VAR')  # VAR=1
    >>> print(var, type(var))
    1 <type 'int'>

:py:func:`envi.get_float` return variable as `float`::

    >>> var = envi.get_float('VAR')  # VAR=1.0
    >>> print(var, type(var))
    1.0 <type 'float'>

EnviManager
===========

You can use the class :py:class:`EnviManager` to automate
the extraction of environment variables with a declarative syntax::

    >>> from envi.manager import EnviManager, EnviType
    >>>
    >>> class EnvBridge(EnviManager):
    ...     MY_STRING = EnviType.string()
    ...     MY_BOOLEAN = EnviType.boolean()
    ...     MY_INT = EnviType.integer()
    ...     MY_FLOAT = EnviType.float()
    ...     MY_JSON = EnviType.generic(cast=json.loads)
    ...
    >>> EnvBridge.configure() # This is when the variables are extracted from the environment
    >>> print(EnvBridge().MY_STRING, type(EnvBridge().MY_STRING)) # You can access the env variables as a property of the singleton
    Value of environment variable MY_STRING <class 'str'>

The :py:class:`EnviManager` class also provides a :py:func:`is_configured` classmethod that returns `True` if the
class was already configured, otherwise it returns False::

    >>> class EnvBridge2(EnviManager):
    ...     MY_VAR = EnviType.string()
    ...
    >>> EnvBridge2.is_configured()
    False
    >>> EnvBridge2.configure()
    >>> EnvBridge2.is_configured()
    True

*NOTE:* The :py:class:`EnviManager` class is a singleton, hence multiple instantiation of the class will return the same object::

    >>> obj1 = EnviBridge()
    >>> obj2 = EnviBridge()
    >>> obj1 is obj2
    True

