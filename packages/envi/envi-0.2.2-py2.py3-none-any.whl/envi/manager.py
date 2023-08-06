"""Manager class for simplified access."""
from envi import get, get_bool, get_float, get_int, get_str


class EnviType(object):
    """Used to configure a subclass of `EnviManager`, defines
    how an environment variable should be retrieved, casted and validated.
    """
    def __init__(self, extractor, cast, required, default, validate, is_ok=None):
        """Initializer
        :param callable extractor: function to be used to extract the variable from
        the environment. It should be one of the functions defined in envi.
        :param callable cast: casting function, see :py:func:`envi.get`
        :param bool required: required flag, see :py:func:`envi.get`
        :param any default: default value, see :py:func:`envi.get`
        :param callable validate: validating function, see :py:func:`envi.get`
        :param list(str) is_ok: truthy string list, see :py:func:`envi.get_bool`
        """
        self.extractor = extractor
        self.cast = cast
        self.required = required
        self.default = default
        self.validate = validate
        self.is_ok = is_ok

    @classmethod
    def generic(cls, cast, required=True, default=None, validate=lambda x: None):
        """Utility initializer for generic environment variable types,
        needs the casting function to be specified

        :param callable cast: casting function, see :py:func:`envi.get`
        :param bool required: required flag, see :py:func:`envi.get`
        :param any default: default value, see :py:func:`envi.get`
        :param callable validate: validating function, see :py:func:`envi.get`

        :return: An `EnviType` instance describing how to retrieve the environment variable
        :rtype: EnviType
        """
        return cls(extractor=get, cast=cast, required=required, default=default, validate=validate)

    @classmethod
    def bool(cls, is_ok=None, required=True, default=None, validate=lambda x: None):
        """Utility initializer for boolean environmental variables.

        :param list(str) is_ok: is_ok: truthy string list, see :py:func:`envi.get_bool`
        :param bool required: required flag, see :py:func:`envi.get`
        :param any default: default value, see :py:func:`envi.get`
        :param callable validate: validating function, see :py:func:`envi.get`

        :return: An `EnviType` instance describing how to retrieve the environment variable
        :rtype: EnviType
        """
        return cls(extractor=get_bool, cast=None, required=required, default=default, validate=validate, is_ok=is_ok)

    @classmethod
    def float(cls, required=True, default=None, validate=lambda x: None):
        """Utility initializer for float environmental variables.

        :param bool required: required flag, see :py:func:`envi.get`
        :param any default: default value, see :py:func:`envi.get`
        :param callable validate: validating function, see :py:func:`envi.get`

        :return: An `EnviType` instance describing how to retrieve the environment variable
        :rtype: EnviType
        """
        return cls(extractor=get_float, cast=None, required=required, default=default, validate=validate)

    @classmethod
    def integer(cls, required=True, default=None, validate=lambda x: None):
        """Utility initializer for int environmental variables.

        :param bool required: required flag, see :py:func:`envi.get`
        :param any default: default value, see :py:func:`envi.get`
        :param callable validate: validating function, see :py:func:`envi.get`

        :return: An `EnviType` instance describing how to retrieve the environment variable
        :rtype: EnviType
        """
        return cls(extractor=get_int, cast=None, required=required, default=default, validate=validate)

    @classmethod
    def string(cls, required=True, default=None, validate=lambda x: None):
        """Utility initializer for string environmental variables.

        :param bool required: required flag, see :py:func:`envi.get`
        :param any default: default value, see :py:func:`envi.get`
        :param callable validate: validating function, see :py:func:`envi.get`

        :return: An `EnviType` instance describing how to retrieve the environment variable
        :rtype: EnviType
        """
        return cls(extractor=get_str, cast=None, required=required, default=default, validate=validate)


class EnviNotConfigured(Exception):
    """Raised if the user tries to access an environment variable
    but the `EnviManager` subclass was not configured yet.
    """
    pass


class EnviAlreadyConfigured(Exception):
    """Raised if the user tries to call :py:func:`EnviManager.configure`
    but the class was already configured."""
    pass


class EnviManager(object):
    """
    Singleton class that will retrieve and hold the values of environment variables
    when :py:func:`EnviManager.configure` is called. The environment variable
    names should be declared as class attributes of type :py:class:`EnviType`.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        """Overrides calls to :py:func:`EnviManager()` to instantiate a new object
        to return the singleton instance instead of a new instance.

        :return: The singleton instance
        :rtype: EnviManager
        :raises EnviNotConfigured: if the class was not configured using :py:func:`EnviType.configure`
        """
        if not isinstance(cls.__instance, cls):
            raise EnviNotConfigured()
        return cls.__instance

    @classmethod
    def is_configured(cls):
        return isinstance(cls.__instance, cls)

    @classmethod
    def configure(cls):
        """Should be called before trying to retrieve the value of environment variables.
        It will instantiate the singleton instance, and for every class attribute
        of type :py:class:`EnviType` it will extract the environment variable
        with the name of the attribute itself, and the value retrieved will be stored
        as attribute in the singleton instance.

        :raises EnviAlreadyConfigured: if called multiple times on the same class.
        """
        if isinstance(cls.__instance, cls):
            raise EnviAlreadyConfigured()
        cls.__instance = object.__new__(cls)
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)
            if isinstance(attribute, EnviType):
                if attribute.cast:
                    value = attribute.extractor(name=attribute_name,
                                                cast=attribute.cast,
                                                required=attribute.required,
                                                default=attribute.default,
                                                validate=attribute.validate,
                                                is_ok=attribute.is_ok)
                else:
                    value = attribute.extractor(name=attribute_name,
                                                required=attribute.required,
                                                default=attribute.default,
                                                validate=attribute.validate,
                                                is_ok=attribute.is_ok)
                setattr(cls.__instance, attribute_name, value)

