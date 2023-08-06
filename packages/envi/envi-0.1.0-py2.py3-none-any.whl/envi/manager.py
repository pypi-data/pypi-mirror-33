"""Manager class for simplified access."""
from envi import get, get_bool, get_float, get_int, get_str


class EnviType(object):
    """Used in the __configuration__ of `EnviManager`, it should be used to
    define how an environment variable should be retrieved, casted and validated.
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

    class EnviMissing(object):
        """Utility class to distinguish missing
        enviroment variables from None/False ones."""
        pass

    Missing = EnviMissing()

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


class EnviUndefined(AttributeError):
    """Raised if the user tries to access an environment variable
    that was not defined in the `__configuration__` attribute of
    the `EnviManager` subclass.
    """
    pass


class EnviNotConfigured(AttributeError):
    """Raised if the user tries to access an environment variable
    but the `EnviManager` subclass was not configured yet.
    """
    pass


class EnviAlreadyConfigured(Exception):
    """Raised if the user tries to call :py:func:`EnviManager.configure`
    but the class was already configured."""
    pass


class EnviMeta(type):
    """Metaclass for `EnviManager`. Overrides the `__getattr__` magic method to
    provide better error handling and direct access to environment variables
    through class attributes
    """
    def __new__(mcs, name, bases, dct):
        """Overridden to add the empty `__values__` dict to the new class.
        Also, the `__configuration__` attribute gets inherited and extended
        by subclasses instead of being overridden."""
        baseconf = {}
        for baseclass in bases:
            if isinstance(baseclass, EnviManager):
                baseconf.update(getattr(baseclass, "__configuration__", {}))
        baseconf.update(dct.get("__configuration__") or {})
        dct["__configuration__"] = baseconf
        dct["__values__"] = {}
        newclass = super(EnviMeta, mcs).__new__(mcs, name, bases, dct)
        return newclass

    def __getattr__(cls, item):
        """Called when the user tries to access an environment variable
        using his class attributes.

        :param item: the name of the environment variable.
        :return: the environment variable named as the `item` attribute.
        :rtype: depending on the `__configuration__`.

        :raises EnviUndefined: if the environment variable was not defined in the `__configuration__`.
        :raises EnviNotConfigured: if the class was not configured yet.
        """
        value = cls.__values__.get(item, EnviType.Missing)
        if value is EnviType.Missing:
            if cls.__configured__:
                msg = "The environment variable {item} was not " \
                      "defined in the class __configuration__".format(item=item)
                raise EnviUndefined(msg)
            else:
                msg = "You need to .configure() the class first."
                raise EnviNotConfigured(msg)
        return value


class EnviManager(metaclass=EnviMeta):
    """This class should be extended from environment bridges/managers.
    When :py:func:`EnviManager.configure` is called, the environmental variables
    are extracted and stored inside the class `__values__` attribute, so they can be
    accessed through class attributes, thanks to the overriding of :py:func:`EnviMeta.__getattr__`.
    """
    __configured__ = False
    __configuration__ = None

    @classmethod
    def configure(cls):
        """Cycles through the `__configuration__` dictionary, where the keys are the environmental
        variables names and the values are `EnviType` instances.
        For each env variable, it uses the `extractor` function to extract them from the environment
        and store them into the class `__values__` attribute as a dict, so their values can be later
        retrieved as class attributes with name corresponding to the variable name.

        :raises EnviAlreadyConfigured: if the class was already configured.
        :raises AttributeError: if `__configuration__` is not properly defined.
        """
        if cls.__configured__ is True:
            raise EnviAlreadyConfigured()
        if not cls.__configuration__ or not isinstance(cls.__configuration__, dict):
            msg = "You need to define the __configuration__ as a dict with the environment " \
                  "variables names as keys and `EnviType`s instances as values"
            raise AttributeError(msg)
        for name, envitype in cls.__configuration__.items():
            if not isinstance(envitype, EnviType):
                msg = "All values in the __configuration__ attribute should be instances of `EnviType`"
                raise AttributeError(msg)
            if envitype.cast:
                cls.__values__[name] = envitype.extractor(name=name,
                                                          cast=envitype.cast,
                                                          required=envitype.required,
                                                          default=envitype.default,
                                                          validate=envitype.validate,
                                                          is_ok=envitype.is_ok)
            else:
                cls.__values__[name] = envitype.extractor(name=name,
                                                          required=envitype.required,
                                                          default=envitype.default,
                                                          validate=envitype.validate,
                                                          is_ok=envitype.is_ok)
        cls.__configured__ = True
