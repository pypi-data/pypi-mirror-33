from past.builtins import basestring
from builtins import object
from copy import copy
from arcana.exception import ArcanaUsageError


class Parameter(object):
    """
    Represents a parameter passed to a Study object

    Parameters
    ----------
    name : str
        Name of the parameter
    value : float | int | str | list | tuple
        Value of the parameter
    """

    def __init__(self, name, value):
        self._name = name
        if value is None:
            self._dtype = None
        else:
            if not isinstance(value, (int, float, str,
                                      tuple, list)):
                raise ArcanaUsageError(
                    "Invalid type for '{}' parameter default ({}), {}, "
                    "can be one of int, float or str"
                    .format(name, value, type(value)))
            self._dtype = (str
                           if isinstance(value, str) else type(value))
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def dtype(self):
        if self._dtype is None:
            return type(None)
        return self._dtype

    def renamed(self, name):
        """
        Duplicate the Parameter and rename it
        """
        duplicate = copy(self)
        duplicate._name = name
        return duplicate

    def __repr__(self):
        return "Parameter(name='{}', value={})".format(self.name,
                                                       self.value)


class ParameterSpec(Parameter):
    """
    Specifies a parameter that can be passed to the study

    Parameters
    ----------
    name : str
        Name of the parameter
    default : float | int | str | list | tuple
        Default value of the parameter
    choices : List(float | int | str | list | tuple)
        Restrict valid inputs to the following choices
    desc : str
        A description of the parameter
    dtype : type | None
        The datatype of the parameter. If none will be determined from
        default value
    """

    def __init__(self, name, default, choices=None, desc=None, dtype=None):
        super(ParameterSpec, self).__init__(name, default)
        self._choices = tuple(choices) if choices is not None else None
        self._desc = desc
        if dtype is not None:
            if self.default is not None and not isinstance(self.default,
                                                           dtype):
                raise ArcanaUsageError(
                    "Provided default value ({}) does not match explicit "
                    "dtype ({})".format(self.default, dtype))
            self._dtype = dtype

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._value

    @property
    def choices(self):
        return self._choices

    @property
    def desc(self):
        return self._desc

    def __repr__(self):
        return ("ParameterSpec(name='{}', default={}, choices={}, "
                "desc='{}')".format(self.name, self.default,
                                    self.choices, self.desc))


class Switch(object):
    """
    A special type parameter that signifies a branch of
    analysis to follow.

    Parameters
    ----------
    name : str
        Name of the parameter
    value : list[str]
        The value of the switch
    """

    def __init__(self, name, value):
        self._name = name
        if not isinstance(value, (basestring, bool)):
            raise ArcanaUsageError(
                "Value of '{}' switch needs to be of type str or bool"
                "(provided {})".format(name, value))
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return "Switch(name='{}', value={})".format(self.name,
                                                    self.value)

    def renamed(self, name):
        """
        Duplicate the Parameter and rename it
        """
        duplicate = copy(self)
        duplicate._name = name
        return duplicate


class SwitchSpec(Switch):
    """
    Specifies a special parameter that switches between different
    methods and/or pipeline input/outputs. Typically used to select
    between comparable methods (e.g. FSL or ANTs registration) but can
    also be used to specify whether certain methods are applied, and by
    extension some auxiliary outputs are generated

    Parameters
    ----------
    name : str
        Name of the parameter
    default : str
        Default option for the switch
    choices : list[str]
        The valid values for the switch
    desc : str
        A description of the parameter
    """

    def __init__(self, name, default, choices=None, desc=None):
        super(SwitchSpec, self).__init__(name, default)
        if self.is_boolean:
            if choices is not None:
                raise ArcanaUsageError(
                    "Choices ({}) are only valid for non-boolean "
                    "switches ('{}')".format("', '".join(choices),
                                               name))
        elif choices is None:
            raise ArcanaUsageError(
                "Choices must be provided for non-boolean "
                "switches ('{}')".format(name))
        self._choices = tuple(choices) if choices is not None else None
        self._desc = desc

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._value

    @property
    def is_boolean(self):
        return isinstance(self.default, bool)

    @property
    def choices(self):
        return self._choices

    def check_valid(self, switch, context=''):
        if self.is_boolean:
            if not isinstance(switch.value, bool):
                raise ArcanaUsageError(
                    "Value provided to switch '{}'{} should be a "
                    "boolean (not {})".format(
                        self.name, context, switch.value))
        elif switch.value not in self.choices:
            raise ArcanaUsageError(
                "Value provided to switch '{}'{} ({}) is not a valid "
                "choice ('{}')".format(
                    self.name, context, switch.value,
                    "', '".join(self.choices)))

    @property
    def desc(self):
        return self._desc

    def __repr__(self):
        return ("SwitchSpec(name='{}', default={}, choices={}, "
                "desc='{}')".format(self.name, self.default,
                                    self.choices, self.desc))
