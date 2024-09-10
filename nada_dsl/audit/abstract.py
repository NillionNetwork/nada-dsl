"""
Abstract interpreter and type definitions for the Nada DSL auditing
component.
"""
# pylint: disable=attribute-defined-outside-init
# pylint: disable=too-many-lines
# pylint: disable=too-few-public-methods
from __future__ import annotations
from typing import Union, Tuple, Sequence
import ast

class Metaclass(type):
    """
    Metaclass for the :obj:`Constant`, :obj:`Public`, and :obj:`Secret`
    classes, enabling comparison of derived classes and conversions
    between them.
    """
    def shape(cls: type, cls_: type = None) -> type:
        """
        Return the shape of a class that is an instance of this
        metaclass.
        
        >>> PublicInteger.shape().__name__
        'Public'
        >>> AbstractInteger.shape(Constant).__name__
        'Integer'
        """
        # pylint: disable=too-many-return-statements
        if cls_ is not None:
            if issubclass(cls, AbstractInteger):
                if cls_ == Constant:
                    return Integer
                if cls_ == Public:
                    return PublicInteger
                if cls_ == Secret:
                    return SecretInteger
            if issubclass(cls, AbstractBoolean):
                if cls_ == Constant:
                    return Boolean
                if cls_ == Public:
                    return PublicBoolean
                if cls_ == Secret:
                    return SecretBoolean

            return None

        if issubclass(cls, Constant):
            return Constant

        if issubclass(cls, Public):
            return Public

        if issubclass(cls, Secret):
            return Secret

        return None

    def __lt__(cls: type, other: type) -> bool:
        if issubclass(cls, Constant):
            return issubclass(other, (Public, Secret))

        if issubclass(cls, Public):
            return issubclass(other, Secret)

        return False

    def __le__(cls: type, other: type) -> bool:
        if issubclass(cls, Public):
            return not issubclass(other, Constant)

        if issubclass(cls, Secret):
            return issubclass(other, Secret)

        return True

class Constant(metaclass=Metaclass):
    """
    Class from which classes for constants are derived.

    >>> Constant <= Constant
    True
    >>> Constant < Secret
    True
    >>> Constant < Secret
    True
    >>> Secret <= Constant
    False
    >>> min(Constant, Public).__name__
    'Constant'
    """

class Public(metaclass=Metaclass):
    """
    Class from which classes for public values are derived.

    >>> Public < Secret
    True
    >>> Public <= Constant
    False
    >>> Public < Public
    False
    >>> min(Secret, Public).__name__
    'Public'
    """

class Secret(metaclass=Metaclass):
    """
    Class from which classes for constants are derived.

    >>> Constant < Secret
    True
    >>> Public < Secret
    True
    >>> Secret < Secret
    False
    >>> max([Secret, Public, Constant]).__name__
    'Secret'
    """

class Abstract(metaclass=Metaclass):
    """
    Base class for abstract interpreter values. All more specific abstract
    value types are derived from this class.
    
    The attributes of this class are also used as global aggregators of the
    signature components (parties, inputs, and outputs) during abstract execution.

    >>> Abstract.initialize()
    >>> party = Party("party")
    >>> input = Input("input", party)
    >>> output = Output(PublicInteger(input), "output", party)
    >>> [
    ...     list(map(lambda entry: type(entry).__name__, component))
    ...     for component in Abstract.signature()
    ... ]
    [['Party'], ['Input'], ['Output']]
    """
    # pylint: disable=missing-function-docstring
    parties = None
    inputs = None
    outputs = None
    context = None
    analysis = None

    @staticmethod
    def initialize(context=None):
        Abstract.parties = []
        Abstract.inputs = []
        Abstract.outputs = []
        Abstract.context = context if context is not None else {}
        Abstract.analysis = {
            'add': 0,
            'mul': 0,
            'cmp': 0,
            'eq': 0,
            'ne': 0,
            'ife': 0
        }

    @staticmethod
    def party(party: Party):
        Abstract.parties.append(party)

    @staticmethod
    def input(input: Input): # pylint: disable=redefined-builtin
        Abstract.inputs.append(input)

    @staticmethod
    def output(output: Output):
        Abstract.outputs.append(output)

    @staticmethod
    def signature() -> Tuple[list[Party], list[Input], list[Output]]:
        return (Abstract.parties, Abstract.inputs, Abstract.outputs)

    def __init__(self: Abstract, cls: type = None):
        self.value = None
        if cls is not None:
            self.__class__ = cls

class Party(Abstract):
    """
    Abstract interpreter values corresponding to parties.

    >>> isinstance(Party("party"), Party)
    True

    If arguments having incorrect types are supplied to the constructor, an
    exception is raised.

    >>> Party(123)
    Traceback (most recent call last):
      ...
    TypeError: name parameter must be a string
    """
    def __init__(self: Party, name: str):
        super().__init__()

        type(self).party(self)

        if not isinstance(name, str):
            raise TypeError('name parameter must be a string')

        self.name = name

class Input(Abstract):
    """
    Abstract interpreter values corresponding to inputs.

    >>> isinstance(Input("input", Party("party")), Input)
    True

    If arguments having incorrect types are supplied to the constructor, an
    exception is raised.

    >>> Input(123, Party("party"))
    Traceback (most recent call last):
      ...
    TypeError: name parameter must be a string
    >>> Input("input", 456)
    Traceback (most recent call last):
      ...
    TypeError: party parameter must be a Party object
    """
    def __init__(self: Input, name: str, party: Party):
        super().__init__()

        type(self).input(self)

        if not isinstance(name, str):
            raise TypeError('name parameter must be a string')

        if not isinstance(party, Party):
            raise TypeError('party parameter must be a Party object')

        self.name = name
        self.party = party

    def _value(self) -> int:
        """
        Retrieve the value for this input when performing concrete interpretation.
        """
        return self.context.get(self.name, None)

class Output(Abstract):
    """
    Abstract interpreter values corresponding to outputs.

    >>> party = Party("party")
    >>> input = Input("input", party)   
    >>> isinstance(Output(PublicInteger(input), "output", party), Output)
    True

    If arguments having incorrect types are supplied to the constructor, an
    exception is raised.

    >>> Output(123, "output", party)
    Traceback (most recent call last):
      ...
    TypeError: output value must be a PublicInteger or a SecretInteger
    >>> Output(PublicInteger(input), 123, party)
    Traceback (most recent call last):
      ...
    TypeError: name parameter must be a string
    >>> Output(PublicInteger(input), "output", 123)
    Traceback (most recent call last):
      ...
    TypeError: party parameter must be a Party object
    """
    def __init__(
            self: Output,
            value: Union[PublicInteger, SecretInteger],
            name: str,
            party: Party
        ):
        super().__init__()

        type(self).output(self)

        if not isinstance(value, (PublicInteger, SecretInteger)):
            raise TypeError('output value must be a PublicInteger or a SecretInteger')

        if not isinstance(name, str):
            raise TypeError('name parameter must be a string')

        if not isinstance(party, Party):
            raise TypeError('party parameter must be a Party object')

        self.value = value
        self.name = name
        self.party = party

        # Store signature in this object (the first such instance constructed)
        # and reset the :obj:`Abstract` class attribute aggregators.
        self.final = (type(self).parties, type(self).inputs, type(self).outputs)
        self.analysis = Abstract.analysis

class AbstractInteger(Abstract):
    """
    Abstract interpreter values corresponding to all integers types.
    This class is only used by derived classes and is not exported.
    """
    def __init__(
            self: Output,
            input: Input = None, # pylint: disable=redefined-builtin
            value: int = None
        ):
        super().__init__()

        self.input = input
        self.value = self.input._value() if input is not None else value
        if input is not None:
            if not hasattr(input, '_type'):
                setattr(input, '_type', None)
            input._type = type(self)

    def __add__(
            self: AbstractInteger,
            other: Union[int, AbstractInteger]
        ) -> AbstractInteger:
        """
        Addition of abstract values that are instances of integer classes.
        The table below presents the output type for each combination
        of argument types.

        +-------------------+-------------------+-------------------+
        |     ``self``      |     ``other``     |    **result**     |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    |    ``Integer``    |    ``Integer``    |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` |    ``Integer``    | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` |    ``Integer``    | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``PublicInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+

        >>> x = Input("x", Party("a"))
        >>> y = Input("y", Party("b"))
        >>> type(PublicInteger(x) + PublicInteger(y)).__name__
        'PublicInteger'
        >>> type(PublicInteger(x) + SecretInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) + PublicInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) + SecretInteger(y)).__name__
        'SecretInteger'

        The addition operator supports ``0`` as a base case in order to
        accommodate the built-in :obj:`sum` function.

        >>> type(sum([PublicInteger(x), SecretInteger(y)])).__name__
        'SecretInteger'
        >>> type(sum([SecretInteger(x), SecretInteger(y)])).__name__
        'SecretInteger'
        >>> type(sum([PublicInteger(x), PublicInteger(y)])).__name__
        'PublicInteger'

        If a value of an incompatible type is supplied to an overloaded
        operator, an exception is raised.

        >>> PublicInteger(x) + 123
        Traceback (most recent call last):
          ...
        TypeError: expecting Integer, PublicInteger, or SecretInteger
        """
        if isinstance(other, int) and other == 0: # Base case for compatibility with :obj:`sum`.
            result = Abstract(type(self))
            result.value = self.value
            return result

        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        result = Abstract(max(type(self), type(other)))

        Abstract.analysis['add'] += 1

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value + other.value

        return result

    def __radd__(
            self: AbstractInteger,
            other: Union[int, AbstractInteger]
        ) -> AbstractInteger:
        """
        Addition for cases in which the left-hand argument is not an instance
        of a class derived from this class.
        """
        return self.__add__(other)

    def __sub__(self: AbstractInteger, other: AbstractInteger) -> AbstractInteger:
        """
        Subtraction of abstract values that are instances of integer classes.
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        result = Abstract(max(type(self), type(other)))

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value - other.value

        return result

    def __rsub__(self: AbstractInteger, other: AbstractInteger) -> AbstractInteger:
        """
        Subtraction for cases in which the left-hand argument is not an instance
        of a class derived from this class.
        """
        return self.__sub__(other)

    def __neg__(self: AbstractInteger) -> AbstractInteger:
        """
        Negation of abstract values that are instances of integer classes.

        >>> x = Input("x", Party("a"))
        >>> type(-Integer(x)).__name__
        'Integer'
        >>> type(-PublicInteger(x)).__name__
        'PublicInteger'
        >>> type(-SecretInteger(x)).__name__
        'SecretInteger'
        """
        result = Abstract(type(self))

        result.value = None
        if self.value is not None:
            result.value = -self.value

        return result

    def __mul__(self: AbstractInteger, other: AbstractInteger) -> AbstractInteger:
        """
        Multipliaction of abstract values that are instances of integer
        classes. The table below presents the output type for each
        combination of argument types.

        +-------------------+-------------------+-------------------+
        |     ``self``      |     ``other``     |    **result**     |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    |    ``Integer``    |    ``Integer``    |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` |    ``Integer``    | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` |    ``Integer``    | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``PublicInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+

        >>> x = Input("x", Party("a"))
        >>> y = Input("y", Party("b"))
        >>> type(PublicInteger(x) + PublicInteger(y)).__name__
        'PublicInteger'
        >>> type(PublicInteger(x) + SecretInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) + PublicInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) + SecretInteger(y)).__name__
        'SecretInteger'

        The addition operator supports ``0`` as a base case in order to
        accommodate the built-in :obj:`sum` function.

        >>> type(sum([PublicInteger(x), SecretInteger(y)])).__name__
        'SecretInteger'
        >>> type(sum([SecretInteger(x), SecretInteger(y)])).__name__
        'SecretInteger'
        >>> type(sum([PublicInteger(x), PublicInteger(y)])).__name__
        'PublicInteger'

        If a value of an incompatible type is supplied to an overloaded
        operator, an exception is raised.

        >>> PublicInteger(x) + 123
        Traceback (most recent call last):
          ...
        TypeError: expecting Integer, PublicInteger, or SecretInteger
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        result = Abstract(max(type(self), type(other)))

        Abstract.analysis['mul'] += 1

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value * other.value

        return result

    def __rmul__(self: AbstractInteger, other: AbstractInteger) -> AbstractInteger:
        """
        Addition for cases in which the left-hand argument is not an instance
        of a class derived from this class.
        """
        return self.__mul__(other)

    def __lt__(self: AbstractInteger, other: AbstractInteger) -> AbstractInteger:
        """
        Comparison of abstract values that are instances of integer
        classes. The table below presents the output type for each
        combination of argument types.

        +-------------------+-------------------+-------------------+
        |     ``self``      |     ``other``     |    **result**     |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    |    ``Integer``    |    ``Boolean``    |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    | ``PublicInteger`` | ``PublicBoolean`` |
        +-------------------+-------------------+-------------------+
        |    ``Integer``    | ``SecretInteger`` | ``SecretBoolean`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` |    ``Integer``    | ``PublicBoolean`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``PublicInteger`` | ``PublicBoolean`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``SecretInteger`` | ``SecretBoolean`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` |    ``Integer``    | ``SecretBoolean`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``PublicInteger`` | ``SecretBoolean`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``SecretInteger`` | ``SecretBoolean`` |
        +-------------------+-------------------+-------------------+

        >>> x = Input("x", Party("a"))
        >>> y = Input("y", Party("b"))
        >>> type(PublicInteger(x) < PublicInteger(y)).__name__
        'PublicBoolean'
        >>> type(PublicInteger(x) < SecretInteger(y)).__name__
        'SecretBoolean'
        >>> type(Integer(x) < Integer(y)).__name__
        'Boolean'
        >>> type(SecretInteger(x) < Integer(y)).__name__
        'SecretBoolean'
        >>> type(Integer(x) < PublicInteger(y)).__name__
        'PublicBoolean'

        If a value of an incompatible type is supplied to an overloaded
        operator, an exception is raised.

        >>> PublicInteger(x) < 123
        Traceback (most recent call last):
          ...
        TypeError: expecting Integer, PublicInteger, or SecretInteger
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        shape = max(type(self), type(other)).shape()
        result = (AbstractBoolean.shape(shape))()
        Abstract.analysis['cmp'] += 1
        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value < other.value

        return result

    def __le__(self: AbstractInteger, other: AbstractInteger) -> AbstractBoolean:
        """
        Comparison of abstract values that are instances of integer
        classes. See :obj:`AbstractInteger.__lt__` for details and examples.
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        shape = max(type(self), type(other)).shape()
        result = (AbstractBoolean.shape(shape))()

        Abstract.analysis['cmp'] += 1

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value <= other.value

        return result

    def __gt__(self: AbstractInteger, other: AbstractInteger) -> AbstractBoolean:
        """
        Comparison of abstract values that are instances of integer
        classes. See :obj:`AbstractInteger.__lt__` for details and examples.
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        shape = max(type(self), type(other)).shape()
        result = (AbstractBoolean.shape(shape))()

        Abstract.analysis['cmp'] += 1

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value > other.value

        return result

    def __ge__(self: AbstractInteger, other: AbstractInteger) -> AbstractBoolean:
        """
        Comparison of abstract values that are instances of integer
        classes. See :obj:`AbstractInteger.__lt__` for details and examples.
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        shape = max(type(self), type(other)).shape()
        result = (AbstractBoolean.shape(shape))()

        Abstract.analysis['cmp'] += 1

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value >= other.value

        return result

    def __eq__(self: AbstractInteger, other: AbstractInteger) -> AbstractBoolean:
        """
        Comparison of abstract values that are instances of integer
        classes. See :obj:`AbstractInteger.__lt__` for details and examples.
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        shape = max(type(self), type(other)).shape()
        result = (AbstractBoolean.shape(shape))()

        Abstract.analysis['eq'] += 1

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value == other.value

        return result

    def __ne__(self: AbstractInteger, other: AbstractInteger) -> AbstractBoolean:
        """
        Comparison of abstract values that are instances of integer
        classes. See :obj:`AbstractInteger.__lt__` for details and examples.
        """
        if not isinstance(other, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        shape = max(type(self), type(other)).shape()
        result = (AbstractBoolean.shape(shape))()

        Abstract.analysis['ne'] += 1

        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value != other.value

        return result

class Integer(AbstractInteger, Constant):
    """
    Abstract values corresponding to constant integers.

    >>> Integer < PublicInteger
    True
    >>> Integer < SecretInteger
    True
    >>> Integer.shape().__name__
    'Constant'

    Instances of this class support the use of some built-in operators.

    >>> x = Input("x", Party("a"))
    >>> y = Input("y", Party("b"))
    >>> type(Integer(x) + Integer(y)).__name__
    'Integer'
    >>> type(Integer(x) * Integer(y)).__name__
    'Integer'
    >>> type(Integer(y) + PublicInteger(x)).__name__
    'PublicInteger'
    >>> type(SecretInteger(x) + Integer(y)).__name__
    'SecretInteger'
    >>> type(PublicInteger(x) * Integer(y)).__name__
    'PublicInteger'
    >>> type(Integer(y) * SecretInteger(x)).__name__
    'SecretInteger'

    The addition operator supports ``0`` as a base case in order to
    accommodate the built-in :obj:`sum` function.

    >>> type(sum([Integer(x), Integer(y)])).__name__
    'Integer'
    >>> type(sum([Integer(x), SecretInteger(y)])).__name__
    'SecretInteger'
    >>> type(sum([PublicInteger(x), Integer(y)])).__name__
    'PublicInteger'

    Concrete interpretation (with explicit values) is also supported if
    those values are present in the aggregate context being maintained
    using the static class attributes.

    >>> Abstract.context = {'x': 123, 'y': 456}
    >>> r = Integer(x, 123) + SecretInteger(y, 456)
    >>> r.value
    579
    >>> r = PublicInteger(x, 123) + Integer(y, 456)
    >>> r.value
    579
    >>> r = SecretInteger(x, 123) * Integer(y, 456)
    >>> r.value
    56088
    >>> r = Integer(x, 123) * PublicInteger(y, 456)
    >>> r.value
    56088

    If a value of an incompatible type is supplied to an overloaded
    operator, an exception is raised.

    >>> Integer(x) + 123
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    >>> Integer(x) * 123
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    >>> 123 * Integer(x)
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    """

class PublicInteger(AbstractInteger, Public):
    """
    Abstract values corresponding to public integers.

    >>> Integer < PublicInteger
    True
    >>> PublicInteger < SecretInteger
    True
    >>> PublicInteger.shape().__name__
    'Public'

    Instances of this class support the use of some built-in operators.

    >>> x = Input("x", Party("a"))
    >>> y = Input("y", Party("b"))
    >>> type(PublicInteger(x) + PublicInteger(y)).__name__
    'PublicInteger'
    >>> type(PublicInteger(x) + SecretInteger(y)).__name__
    'SecretInteger'
    >>> type(SecretInteger(x) + PublicInteger(y)).__name__
    'SecretInteger'
    >>> type(PublicInteger(x) * PublicInteger(y)).__name__
    'PublicInteger'
    >>> type(PublicInteger(x) * SecretInteger(y)).__name__
    'SecretInteger'
    >>> type(SecretInteger(x) * PublicInteger(y)).__name__
    'SecretInteger'

    The addition operator supports ``0`` as a base case in order to
    accommodate the built-in :obj:`sum` function.

    >>> type(sum([PublicInteger(x), SecretInteger(y)])).__name__
    'SecretInteger'
    >>> type(sum([PublicInteger(x), PublicInteger(y)])).__name__
    'PublicInteger'

    Concrete interpretation (with explicit values) is also supported if
    those values are present in the aggregate context being maintained
    using the static class attributes.

    >>> Abstract.context = {'x': 123, 'y': 456}
    >>> r = PublicInteger(x, 123) + SecretInteger(y, 456)
    >>> r.value
    579
    >>> r = PublicInteger(x, 123) + PublicInteger(y, 456)
    >>> r.value
    579
    >>> r = PublicInteger(x, 123) * SecretInteger(y, 456)
    >>> r.value
    56088
    >>> r = PublicInteger(x, 123) * PublicInteger(y, 456)
    >>> r.value
    56088

    If a value of an incompatible type is supplied to an overloaded
    operator, an exception is raised.

    >>> PublicInteger(x) + 123
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    >>> PublicInteger(x) * 123
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    >>> 123 * PublicInteger(x)
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    """

class SecretInteger(AbstractInteger, Secret):
    """
    Abstract interpreter values corresponding to secret integers.

    >>> SecretInteger < Integer
    False
    >>> PublicInteger < SecretInteger
    True
    >>> SecretInteger.shape().__name__
    'Secret'

    Instances of this class support the use of some built-in operators.

    >>> x = Input("x", Party("a"))
    >>> y = Input("y", Party("b"))
    >>> type(Integer(x) + SecretInteger(y)).__name__
    'SecretInteger'
    >>> type(SecretInteger(x) + PublicInteger(y)).__name__
    'SecretInteger'
    >>> type(SecretInteger(x) + SecretInteger(y)).__name__
    'SecretInteger'
    >>> type(PublicInteger(x) * SecretInteger(y)).__name__
    'SecretInteger'
    >>> type(SecretInteger(x) * Integer(y)).__name__
    'SecretInteger'
    >>> type(SecretInteger(x) * SecretInteger(y)).__name__
    'SecretInteger'

    Concrete interpretation (with explicit values) is also supported if
    those values are present in the aggregate context being maintained
    using the static class attributes.

    >>> Abstract.context = {'x': 123, 'y': 456}
    >>> r = SecretInteger(x, 123) * SecretInteger(y, 456)
    >>> r.value
    56088

    If a value of an incompatible type is supplied to an overloaded
    operator, an exception is raised.

    >>> SecretInteger(x) + 123
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    >>> SecretInteger(x) * 123
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    >>> 123 * SecretInteger(x)
    Traceback (most recent call last):
      ...
    TypeError: expecting Integer, PublicInteger, or SecretInteger
    """

class AbstractBoolean(Abstract):
    """
    Abstract interpreter values corresponding to all boolean types.
    This class is only used by derived classes and is not exported.
    """
    def __init__(
            self: Output,
            input: Input = None, # pylint: disable=redefined-builtin
            value: int = None
        ):
        super().__init__()

        self.input = input
        self.value = self.input._value() if input is not None else value
        if input is not None:
            if not hasattr(input, '_type'):
                setattr(input, '_type', None)
            input._type = type(self)

    def if_else(
            self: AbstractBoolean,
            true: AbstractInteger,
            false: AbstractInteger
        ) -> AbstractInteger:
        """
        Ternary (*i.e.*, conditional) operator. The table below presents
        the output type for each combination of argument types.

        +-------------------+------------------------+-------------------+
        |     ``self``      | ``true`` and ``false`` |    **result**     |
        +-------------------+------------------------+-------------------+
        |    ``Boolean``    |      ``Integer``       |    ``Integer``    |
        +-------------------+------------------------+-------------------+
        |    ``Boolean``    |   ``PublicInteger``    | ``PublicInteger`` |
        +-------------------+------------------------+-------------------+
        |    ``Boolean``    |   ``SecretInteger``    | ``SecretInteger`` |
        +-------------------+------------------------+-------------------+
        | ``PublicBoolean`` |      ``Integer``       | ``PublicInteger`` |
        +-------------------+------------------------+-------------------+
        | ``PublicBoolean`` |   ``PublicInteger``    | ``PublicInteger`` |
        +-------------------+------------------------+-------------------+
        | ``PublicBoolean`` |   ``SecretInteger``    | ``SecretInteger`` |
        +-------------------+------------------------+-------------------+
        | ``SecretBoolean`` |      ``Integer``       | ``SecretInteger`` |
        +-------------------+------------------------+-------------------+
        | ``SecretBoolean`` |   ``PublicInteger``    | ``SecretInteger`` |
        +-------------------+------------------------+-------------------+
        | ``SecretBoolean`` |   ``SecretInteger``    | ``SecretInteger`` |
        +-------------------+------------------------+-------------------+

        >>> x = Input("x", Party("a"))
        >>> y = Input("y", Party("b"))
        >>> z = Input("z", Party("c"))
        >>> type(PublicBoolean(x).if_else(PublicInteger(y), PublicInteger(z))).__name__
        'PublicInteger'

        If a value of an incompatible type is supplied to an overloaded
        operator, an exception is raised.

        >>> PublicInteger(x) + 123
        Traceback (most recent call last):
          ...
        TypeError: expecting Integer, PublicInteger, or SecretInteger
        """
        if not isinstance(true, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        if not isinstance(false, (Integer, PublicInteger, SecretInteger)):
            raise TypeError('expecting Integer, PublicInteger, or SecretInteger')

        shape = max([type(self), type(true), type(false)]).shape()
        result = (AbstractInteger.shape(shape))()

        Abstract.analysis['ife'] += 1

        result.value = None
        if self.value is not None and true.value is not None and false.value is not None:
            result.value = true.value if self.value else false.value

        return result

class Boolean(AbstractBoolean, Constant):
    """
    Abstract values corresponding to constant boolean values.
    """

class PublicBoolean(AbstractBoolean, Public):
    """
    Abstract values corresponding to public boolean values.
    """

class SecretBoolean(AbstractBoolean, Secret):
    """
    Abstract values corresponding to secret boolean values.
    """

def signature(source: str) -> Tuple[list[Party], list[Input], list[Output]]:
    """
    Return the signature of the supplied Nada program (represented as a
    string). The signature consists of three lists: the program's (1) parties,
    (2) inputs, and (3) outputs.

    >>> source = '\\n'.join([
    ...     'from nada_dsl import *',
    ...     '',
    ...     'def nada_main():',
    ...     '    party1 = Party(name="Party1")',
    ...     '    a = SecretInteger(Input(name="a", party=party1))',
    ...     '    b = SecretInteger(Input(name="b", party=party1))',
    ...     '',
    ...     '    c = a * b',
    ...     '',
    ...     '    return [Output(c, "c", party1), Output(c, "d", party1)]'
    ... ])
    >>> (ps, ins, outs) = signature(source)
    >>> [p.name for p in ps]
    ['Party1']
    >>> [i.name for i in ins]
    ['a', 'b']
    >>> [o.name for o in outs]
    ['c', 'd']

    If the supplied strign is not a valid Nada program, an exception is raised.

    >>> source = '\\n'.join([
    ...     'from nada_dsl import *',
    ...     'def nada_main():',
    ...     '    pass'
    ... ])
    >>> signature(source)
    Traceback (most recent call last):
      ...
    ValueError: nada_main must return a sequence of outputs
    >>> source = '\\n'.join([
    ...     'def nada_main():',
    ...     '    pass'
    ... ])
    >>> signature(source)
    Traceback (most recent call last):
      ...
    ValueError: first statement must be: from nada_dsl import *
    >>> source = '\\n'.join([
    ...     'from nada_dsl import *',
    ...     'def foo():',
    ...     '    pass'
    ... ])
    >>> signature(source)
    Traceback (most recent call last):
      ...
    ValueError: nada_main must be defined
    """
    root = ast.parse(source)

    if (
      len(root.body) == 0 or
      not isinstance(root.body[0], ast.ImportFrom) or
      len(root.body[0].names) != 1 or
      root.body[0].names[0].name != '*' or
      root.body[0].module != 'nada_dsl'
    ):
        raise ValueError('first statement must be: from nada_dsl import *')

    # Adjust the import statement and add a statement that resets the static
    # class attributes being used for aggregation.
    root.body[0].module = 'nada_dsl.audit'
    #root.body.append(ast.Expr(ast.Call(ast.Name('nada_main', ast.Load()), [], [])))
    root.body.append(
        ast.Expr(
            ast.Call(
                ast.Attribute(ast.Name('Abstract', ast.Load()), 'initialize', ast.Load()),
                [],
                []
            )
        )
    )
    ast.fix_missing_locations(root)

    # Execute the program (introducing the main function into the context).
    context = {}
    exec(compile(root, '', 'exec'), context) # pylint: disable=exec-used
    if 'nada_main' not in context:
        raise ValueError('nada_main must be defined')

    # Perform abstract execution of the main function and return the signature of
    # the result.
    outputs = context['nada_main']()
    if (
        isinstance(outputs, Sequence) and
        len(outputs) > 0 and
        all(isinstance(output, Output) for output in outputs)
    ):
        return Abstract.signature()

    raise ValueError('nada_main must return a sequence of outputs')
