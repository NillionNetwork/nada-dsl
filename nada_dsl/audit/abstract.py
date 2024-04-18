"""
Abstract interpreter for Nada DSL.
"""
from __future__ import annotations
from typing import Union, Tuple, Sequence
import ast

class Abstract:
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

    @staticmethod
    def initialize():
        Abstract.parties = []
        Abstract.inputs = []
        Abstract.outputs = []
        Abstract.context = {}

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

    def __init__(self, cls=None):
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

class PublicInteger(Abstract):
    """
    Abstract interpreter values corresponding to public integers.

    >>> x = Input('x', Party('a'))
    >>> y = Input('y', Party('b'))
    >>> type(PublicInteger(x) + SecretInteger(y)).__name__
    'SecretInteger'

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
    >>> r = SecretInteger(x, 123) + SecretInteger(y, 456)
    >>> r.value
    579
    >>> r = PublicInteger(x, 123) * SecretInteger(y, 456)
    >>> r.value
    56088
    >>> r = PublicInteger(x, 123) * PublicInteger(y, 456)
    >>> r.value
    56088
    """
    def __init__(
            self: Output,
            input: Input = None, # pylint: disable=redefined-builtin
            value: int = None
        ):
        super().__init__()

        self.input = input
        self.value = self.input._value() if input is not None else value

    def __add__(
            self: PublicInteger,
            other: Union[PublicInteger, SecretInteger]
        ) -> Union[PublicInteger, SecretInteger]:
        """
        The table below presents the output type for each combination
        of argument types.

        +-------------------+-------------------+-------------------+
        |     ``self``      |     ``other``     |    **result**     |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``SecretInteger`` | ``SecretInteger`` |
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
        TypeError: expecting PublicInteger or SecretInteger
        """
        if other == 0: # Base case for ``sum``.
            result = Abstract(PublicInteger)
            result.value = self.value
            return result

        if isinstance(other, PublicInteger):
            result = Abstract(PublicInteger)
            result.value = None
            if self.value is not None and other.value is not None:
                result.value = self.value + other.value
            return result

        if isinstance(other, SecretInteger):
            result = Abstract(SecretInteger)
            result.value = None
            if self.value is not None and other.value is not None:
                result.value = self.value + other.value
            return result

        raise TypeError('expecting PublicInteger or SecretInteger')

    def __radd__(
            self: PublicInteger,
            other: Union[PublicInteger, SecretInteger]
        ) -> Union[PublicInteger, SecretInteger]:
        return self.__add__(other)

    def __mul__(
            self: PublicInteger,
            other: Union[PublicInteger, SecretInteger]
        ) -> Union[PublicInteger, SecretInteger]:
        """
        The table below presents the output type for each combination
        of argument types.

        +-------------------+-------------------+-------------------+
        |     ``self``      |     ``other``     |    **result**     |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``PublicInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+

        >>> x = Input("x", Party("a"))
        >>> y = Input("y", Party("b"))
        >>> type(PublicInteger(x) * PublicInteger(y)).__name__
        'PublicInteger'
        >>> type(PublicInteger(x) * SecretInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) * PublicInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) * SecretInteger(y)).__name__
        'SecretInteger'

        If a value of an incompatible type is supplied to an overloaded
        operator, an exception is raised.

        >>> PublicInteger(x) * 123
        Traceback (most recent call last):
          ...
        TypeError: expecting PublicInteger or SecretInteger
        >>> 123 * PublicInteger(x)
        Traceback (most recent call last):
          ...
        TypeError: expecting PublicInteger or SecretInteger
        """
        if isinstance(other, PublicInteger):
            result = Abstract(PublicInteger)
            result.value = None
            if self.value is not None and other.value is not None:
                result.value = self.value * other.value
            return result

        if isinstance(other, SecretInteger):
            result = Abstract(SecretInteger)
            result.value = None
            if self.value is not None and other.value is not None:
                result.value = self.value * other.value
            return result

        raise TypeError('expecting PublicInteger or SecretInteger')

    def __rmul__(self: PublicInteger, other: Union[PublicInteger, SecretInteger]):
        return self.__mul__(other)

class SecretInteger(Abstract):
    """
    Abstract interpreter values corresponding to secret integers.

    >>> x = Input('x', Party('a'))
    >>> y = Input('y', Party('b'))
    >>> type(PublicInteger(x) + SecretInteger(y)).__name__
    'SecretInteger'

    Concrete interpretation (with explicit values) is also supported if
    those values are present in the aggregate context being maintained
    using the static class attributes.

    >>> Abstract.context = {'x': 123, 'y': 456}
    >>> r = SecretInteger(x, 123) * SecretInteger(y, 456)
    >>> r.value
    56088
    """
    def __init__(
            self: Output,
            input: Input = None, # pylint: disable=redefined-builtin
            value: int = None
        ):
        super().__init__()

        self.input = input
        self.value = self.input._value() if input is not None else value

    def __add__(
            self: SecretInteger,
            other: Union[PublicInteger, SecretInteger]
        ) -> Union[PublicInteger, SecretInteger]:
        """
        The table below presents the output type for each combination
        of argument types.

        +-------------------+-------------------+-------------------+
        |     ``self``      |     ``other``     |    **result**     |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``SecretInteger`` | ``SecretInteger`` |
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

        If a value of an incompatible type is supplied to an overloaded
        operator, an exception is raised.

        >>> SecretInteger(x) + 123
        Traceback (most recent call last):
          ...
        TypeError: expecting PublicInteger or SecretInteger
        """
        if other == 0: # Base case for ``sum``.
            result = Abstract(SecretInteger)
            result.value = self.value
            return result

        if not isinstance(other, (PublicInteger, SecretInteger)):
            raise TypeError('expecting PublicInteger or SecretInteger')

        result = Abstract(SecretInteger)
        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value + other.value
        return result

    def __radd__(
            self: PublicInteger,
            other: Union[PublicInteger, SecretInteger]
        ) -> Union[PublicInteger, SecretInteger]:
        return self.__add__(other)

    def __mul__(
            self: SecretInteger,
            other: Union[PublicInteger, SecretInteger]
        ) -> Union[PublicInteger, SecretInteger]:
        """
        The table below presents the output type for each combination
        of argument types.

        +-------------------+-------------------+-------------------+
        |     ``self``      |     ``other``     |    **result**     |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``PublicInteger`` | ``PublicInteger`` |
        +-------------------+-------------------+-------------------+
        | ``PublicInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``PublicInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+
        | ``SecretInteger`` | ``SecretInteger`` | ``SecretInteger`` |
        +-------------------+-------------------+-------------------+

        >>> x = Input("x", Party("a"))
        >>> y = Input("y", Party("b"))
        >>> type(PublicInteger(x) * PublicInteger(y)).__name__
        'PublicInteger'
        >>> type(PublicInteger(x) * SecretInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) * PublicInteger(y)).__name__
        'SecretInteger'
        >>> type(SecretInteger(x) * SecretInteger(y)).__name__
        'SecretInteger'

        If a value of an incompatible type is supplied to an overloaded
        operator, an exception is raised.

        >>> SecretInteger(x) * 123
        Traceback (most recent call last):
          ...
        TypeError: expecting PublicInteger or SecretInteger
        >>> 123 * SecretInteger(x)
        Traceback (most recent call last):
          ...
        TypeError: expecting PublicInteger or SecretInteger
        """
        if not isinstance(other, (PublicInteger, SecretInteger)):
            raise TypeError('expecting PublicInteger or SecretInteger')

        result = Abstract(SecretInteger)
        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value * other.value
        return result

    def __rmul__(
            self: PublicInteger,
            other: Union[PublicInteger, SecretInteger]
        ) -> Union[PublicInteger, SecretInteger]:
        return self.__mul__(other)

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
