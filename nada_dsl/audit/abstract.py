"""
Abstract interpreter for Nada DSL.
"""
from __future__ import annotations
from typing import Union
import ast

class Abstract:
    """
    Base class for abstract interpreter values.
    """
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
    def party(argument):
        Abstract.parties.append(argument)

    @staticmethod
    def input(argument):
        Abstract.inputs.append(argument)

    @staticmethod
    def output(argument):
        Abstract.outputs.append(argument)

    def __init__(self, cls=None):
        self.value = None
        if cls is not None:
            self.__class__ = cls

class Party(Abstract):
    """
    Abstract interpreter values corresponding to parties.
    """
    def __init__(self: Party, name: str):
        type(self).party(self)

        if not isinstance(name, str):
            raise TypeError('name parameter must be a string')

        self.name = name

class Input(Abstract):
    """
    Abstract interpreter values corresponding to inputs.
    """
    def __init__(self: Input, name: str, party: Party):
        type(self).input(self)

        if not isinstance(name, str):
            raise TypeError('name parameter must be a string')

        if not isinstance(name, str):
            raise TypeError('party parameter must be a Party object')

        self.name = name
        self.party = party

    def value(self):
        return self.context.get(self.name, None)

class Output(Abstract):
    """
    Abstract interpreter values corresponding to outputs.
    """
    def __init__(
            self: Output,
            value: Union[PublicInteger, SecretInteger],
            name: str,
            party: Party
        ):
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
        type(self).parties = []
        type(self).inputs = []
        type(self).outputs = []

class PublicInteger(Abstract):
    """
    Abstract interpreter values corresponding to public integers.
    """
    def __init__(self: Output, input: Input = None, value: int = None):
        self.input = input
        self.value = self.input.value() if input is not None else value

    def __add__(self: PublicInteger, other: Union[PublicInteger, SecretInteger]):
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

    def __radd__(self: PublicInteger, other: Union[PublicInteger, SecretInteger]):
        return self.__add__(other)

    def __mul__(self: PublicInteger, other: Union[PublicInteger, SecretInteger]):
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
    """
    def __init__(self: Output, input: Input = None, value: int = None):
        self.input = input
        self.value = self.input.value() if input is not None else value

    def __add__(self: SecretInteger, other: Union[PublicInteger, SecretInteger]):
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

    def __radd__(self: PublicInteger, other: Union[PublicInteger, SecretInteger]):
        return self.__add__(other)

    def __mul__(self: SecretInteger, other: Union[PublicInteger, SecretInteger]):
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
        """
        if not isinstance(other, (PublicInteger, SecretInteger)):
            raise TypeError('expecting PublicInteger or SecretInteger')

        result = Abstract(SecretInteger)
        result.value = None
        if self.value is not None and other.value is not None:
            result.value = self.value * other.value
        return result

    def __rmul__(self: PublicInteger, other: Union[PublicInteger, SecretInteger]):
        return self.__mul__(other)

def signature(source: str):
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
    ValueError: nada_main must return a list of outputs
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

    root.body[0].module = 'nada_dsl.audit'
    #root.body.append(ast.Expr(ast.Call(ast.Name('nada_main', ast.Load()), [], [])))
    ast.fix_missing_locations(root)
    Abstract.initialize()
    context = {}
    exec(compile(root, '', 'exec'), context)

    if 'nada_main' not in context:
        raise ValueError('nada_main must be defined')
    
    result = context['nada_main']()

    if result is not None and len(result) > 0 and isinstance(result[0], Output):
        o = result[0]
        sig = (o.final[0], o.final[1], result)
        return sig

    raise ValueError('nada_main must return a list of outputs')
