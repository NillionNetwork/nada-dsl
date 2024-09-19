import itertools
from collections.abc import Iterable
from typing import Union

import pytest

from nada_dsl import Input, Party
from nada_dsl.nada_types import BaseType, Mode
from nada_dsl.nada_types.scalar_types import Integer, PublicInteger, SecretInteger, Boolean, PublicBoolean, \
    SecretBoolean, UnsignedInteger, PublicUnsignedInteger, SecretUnsignedInteger, ScalarType, BooleanType


def combine_lists(list1, list2):
    """This returns all combinations for the items of two lists"""
    result = []
    for item1 in list1:
        if isinstance(item1, Iterable):
            item1 = list(item1)
        else:
            item1 = [item1]
        for item2 in list2:
            if isinstance(item2, Iterable):
                item2 = list(item2)
            else:
                item2 = [item2]
            result.append(item1 + item2)
    return result


# All boolean values
booleans = [
    Boolean(value=True),
    PublicBoolean(Input(name="public", party=Party("party"))),
    SecretBoolean(Input(name="secret", party=Party("party")))
]

# All public boolean values
public_booleans = [
    Boolean(value=True),
    PublicBoolean(Input(name="public", party=Party("party"))),
]

# All secret boolean values
secret_booleans = [SecretBoolean(Input(name="secret", party="party"))]

# All integer values
integers = [
    Integer(value=1),
    PublicInteger(Input(name="public", party=Party("party"))),
    SecretInteger(Input(name="secret", party=Party("party")))
]

# All public integer values
public_integers = [
    Integer(value=1),
    PublicInteger(Input(name="public", party=Party("party"))),
]

# All secret integer values
secret_integers = [SecretInteger(Input(name="secret", party="party"))]

# All integer inputs (non literal elements)
variable_integers = [
    PublicInteger(Input(name="public", party=Party("party"))),
    SecretInteger(Input(name="public", party=Party("party")))
]

# All unsigned integer values
unsigned_integers = [
    UnsignedInteger(value=1),
    PublicUnsignedInteger(Input(name="public", party=Party("party"))),
    SecretUnsignedInteger(Input(name="secret", party=Party("party")))
]

# All public unsigned integer values
public_unsigned_integers = [
    UnsignedInteger(value=1),
    PublicUnsignedInteger(Input(name="public", party=Party("party"))),
]

# All secret unsigned integer values
secret_unsigned_integers = [SecretUnsignedInteger(Input(name="secret", party="party"))]

# All unsigned integer inputs (non-literal elements)
variable_unsigned_integers = [
    PublicUnsignedInteger(Input(name="public", party=Party("party"))),
    SecretUnsignedInteger(Input(name="public", party=Party("party")))
]

# Binary arithmetic operations. They are provided as functions to the tests to avoid duplicate code
binary_arithmetic_functions = [
    lambda lhs, rhs: lhs + rhs,
    lambda lhs, rhs: lhs - rhs,
    lambda lhs, rhs: lhs * rhs,
    lambda lhs, rhs: lhs / rhs,
    lambda lhs, rhs: lhs % rhs,
]

# Data set for the binary arithmetic operation tests. It combines all allowed operands with the operations.
binary_arithmetic_operations = (
    # Integers
        combine_lists(itertools.product(integers, repeat=2), binary_arithmetic_functions)
        # UnsignedIntegers
        + combine_lists(itertools.product(unsigned_integers, repeat=2), binary_arithmetic_functions)
)


@pytest.mark.parametrize("left, right, operation", binary_arithmetic_operations)
def test_binary_arithmetic_operations(left: ScalarType, right: ScalarType, operation):
    result = operation(left, right)
    assert result.base_type, left.base_type
    assert result.base_type, right.base_type
    assert result.mode.value, max([left.mode.value, right.mode.value])


# Allowed operands for the power operation
allowed_pow_operands = (
        # Integers: Only combinations of public integers
        combine_lists(public_integers, public_integers)
        # UnsignedIntegers: Only combinations of public unsigned integers
        + combine_lists(public_unsigned_integers, public_unsigned_integers)
)


@pytest.mark.parametrize("left, right", allowed_pow_operands)
def test_pow(left: ScalarType, right: ScalarType):
    result = left ** right
    assert result.base_type, left.base_type
    assert result.base_type, right.base_type
    assert result.mode.value, max([left.mode.value, right.mode.value])


# All shift operations.
shift_functions = [
    lambda lhs, rhs: lhs << rhs,
    lambda lhs, rhs: lhs >> rhs,
]

# The shift operations accept public unsigned integers on the right operand only.
allowed_shift_operands = (
        # Integers on the left operand
        combine_lists(combine_lists(integers, public_unsigned_integers), shift_functions)
        # UnsignedIntegers on the left operand
        + combine_lists(combine_lists(unsigned_integers, public_unsigned_integers), shift_functions)
)


@pytest.mark.parametrize("left, right, operation", allowed_shift_operands)
def test_shift(left: ScalarType, right: ScalarType, operation):
    result = operation(left, right)
    assert result.base_type, left.base_type
    assert result.mode, left.mode


# Binary relational operations.
# Equals and NotEquals are not included, because they accept by the Boolean types as well
binary_relational_functions = [
    lambda lhs, rhs: lhs < rhs,
    lambda lhs, rhs: lhs > rhs,
    lambda lhs, rhs: lhs <= rhs,
    lambda lhs, rhs: lhs >= rhs
]

# Allowed operands that are accepted by the numeric relational operations. They are combined with the operations.
binary_relational_operations = (
        # Integers
        combine_lists(itertools.product(integers, repeat=2), binary_relational_functions)
        # UnsignedIntegers
        + combine_lists(itertools.product(unsigned_integers, repeat=2), binary_relational_functions)
)


@pytest.mark.parametrize("left, right, operation", binary_relational_operations)
def test_binary_relational_operations(left: ScalarType, right: ScalarType, operation):
    result = operation(left, right)
    assert result.base_type, BaseType.BOOLEAN
    assert result.mode.value, max([left.mode.value, right.mode.value])


# Equality operations
equals_functions = [
    lambda lhs, rhs: lhs == rhs,
    lambda lhs, rhs: lhs != rhs
]

# Allowed operands that are accepted by the equality operations. They are combined with the operations.
equals_operations = (
        combine_lists(itertools.product(integers, repeat=2), equals_functions)
        + combine_lists(itertools.product(unsigned_integers, repeat=2), equals_functions)
        + combine_lists(itertools.product(booleans, repeat=2), equals_functions)
)


@pytest.mark.parametrize("left, right, operation", equals_operations)
def test_equals_operations(left: ScalarType, right: ScalarType, operation):
    result = operation(left, right)
    assert result.base_type, BaseType.BOOLEAN
    assert result.mode.value, max([left.mode.value, right.mode.value])


# Allowed operands that are accepted by the public_equals function. Literals are not accepted.
public_equals_operands = (
        # Integers
        combine_lists(variable_integers, variable_integers)
        # UnsignedIntegers
        + combine_lists(variable_unsigned_integers, variable_unsigned_integers)
)


@pytest.mark.parametrize("left, right", public_equals_operands)
def test_public_equals(
        left: Union["PublicInteger", "SecretInteger", "PublicUnsignedInteger", "SecretUnsignedInteger"]
        , right: Union["PublicInteger", "SecretInteger", "PublicUnsignedInteger", "SecretUnsignedInteger"]
):
    assert isinstance(left.public_equals(right), PublicBoolean)


# All supported logic functions
logic_functions = [
    lambda lhs, rhs: lhs & rhs,
    lambda lhs, rhs: lhs | rhs,
    lambda lhs, rhs: lhs ^ rhs
]

# Allowed operands that are accepted by the logic operations. They are combined with the operations.
binary_logic_operations = combine_lists(combine_lists(booleans, booleans), logic_functions)


@pytest.mark.parametrize("left, right, operation", binary_logic_operations)
def test_logic_operations(left: BooleanType, right: BooleanType, operation):
    result = operation(left, right)
    assert result.base_type, BaseType.BOOLEAN
    assert result.mode.value, max([left.mode.value, right.mode.value])


@pytest.mark.parametrize("operand", booleans)
def test_invert_operations(operand):
    result = ~operand
    assert result.base_type, BaseType.BOOLEAN
    assert result.mode, operand.mode


# Allowed operands that are accepted by the probabilistic truncation.
trunc_pr_operands = (
        combine_lists(secret_integers, public_unsigned_integers)
        + combine_lists(secret_unsigned_integers, public_unsigned_integers)
)


@pytest.mark.parametrize("left, right", trunc_pr_operands)
def test_trunc_pr(left, right):
    result = left.trunc_pr(right)
    assert result.base_type, left.base_type
    assert result.mode, Mode.SECRET


# Allowed types that can generate a random value.
random_operands = secret_integers + secret_unsigned_integers


@pytest.mark.parametrize("operand", random_operands)
def test_random(operand):
    result = operand.random()
    assert result.base_type, operand.base_type
    assert result.mode, Mode.SECRET


# Allowed types that can invoke the to_public() function.
to_public_operands = secret_integers + secret_unsigned_integers + secret_booleans


@pytest.mark.parametrize("operand", to_public_operands)
def test_to_public(operand):
    result = operand.to_public()
    assert result.base_type, operand.base_type
    assert result.mode, Mode.PUBLIC


public_boolean = PublicBoolean(Input(name="public", party="party"))

# Allow combination of operands that are accepted by if_else function
if_else_operands = (
        combine_lists(secret_booleans, combine_lists(integers, integers))
        + combine_lists([public_boolean], combine_lists(integers, integers))
        + combine_lists(secret_booleans, combine_lists(unsigned_integers, unsigned_integers))
        + combine_lists([public_boolean], combine_lists(unsigned_integers, unsigned_integers))
)


@pytest.mark.parametrize("condition, left, right", if_else_operands)
def test_if_else(condition: BooleanType, left: ScalarType, right: ScalarType):
    result = condition.if_else(left, right)
    assert left.base_type == right.base_type
    assert result.base_type == left.base_type
    expected_mode = Mode(max([condition.mode.value, left.mode.value, right.mode.value]))
    assert result.mode, expected_mode


# List of not allowed operations
not_allowed_binary_operations = \
    (  # Arithmetic operations
            combine_lists(combine_lists(booleans, booleans), binary_arithmetic_functions)
            + combine_lists(combine_lists(booleans, integers), binary_arithmetic_functions)
            + combine_lists(combine_lists(booleans, unsigned_integers), binary_arithmetic_functions)
            + combine_lists(combine_lists(integers, booleans), binary_arithmetic_functions)
            + combine_lists(combine_lists(integers, unsigned_integers), binary_arithmetic_functions)
            + combine_lists(combine_lists(unsigned_integers, booleans), binary_arithmetic_functions)
            + combine_lists(combine_lists(unsigned_integers, integers), binary_arithmetic_functions)
            # Relational operations
            + combine_lists(combine_lists(booleans, booleans), binary_relational_functions)
            + combine_lists(combine_lists(booleans, integers), binary_relational_functions)
            + combine_lists(combine_lists(booleans, unsigned_integers), binary_relational_functions)
            + combine_lists(combine_lists(integers, booleans), binary_relational_functions)
            + combine_lists(combine_lists(integers, unsigned_integers), binary_relational_functions)
            + combine_lists(combine_lists(unsigned_integers, booleans), binary_relational_functions)
            + combine_lists(combine_lists(unsigned_integers, integers), binary_relational_functions)
            # Equals operations
            + combine_lists(combine_lists(booleans, integers), equals_functions)
            + combine_lists(combine_lists(booleans, unsigned_integers), equals_functions)
            + combine_lists(combine_lists(integers, booleans), equals_functions)
            + combine_lists(combine_lists(integers, unsigned_integers), equals_functions)
            + combine_lists(combine_lists(unsigned_integers, booleans), equals_functions)
            + combine_lists(combine_lists(unsigned_integers, integers), equals_functions)
            # Logic operations
            + combine_lists(combine_lists(booleans, integers), logic_functions)
            + combine_lists(combine_lists(booleans, unsigned_integers), logic_functions)
            + combine_lists(combine_lists(integers, booleans), logic_functions)
            + combine_lists(combine_lists(integers, integers), logic_functions)
            + combine_lists(combine_lists(integers, unsigned_integers), logic_functions)
            + combine_lists(combine_lists(unsigned_integers, booleans), logic_functions)
            + combine_lists(combine_lists(unsigned_integers, integers), logic_functions)
            + combine_lists(combine_lists(unsigned_integers, unsigned_integers), logic_functions)
    )


@pytest.mark.parametrize("left, right, operation", not_allowed_binary_operations)
def test_not_allowed_binary_operations(left, right, operation):
    with pytest.raises(Exception) as invalid_operation:
        operation(left, right)
    assert invalid_operation.type == TypeError


# List of operands that the operation power does not accept.
not_allowed_pow = (
        combine_lists(booleans, booleans)
        + combine_lists(integers, booleans)
        + combine_lists(unsigned_integers, booleans)
        + combine_lists(booleans, integers)
        + combine_lists(secret_integers, integers)
        + combine_lists(public_integers, secret_integers)
        + combine_lists(integers, unsigned_integers)
        + combine_lists(booleans, unsigned_integers)
        + combine_lists(unsigned_integers, integers)
        + combine_lists(secret_unsigned_integers, unsigned_integers)
        + combine_lists(public_unsigned_integers, secret_unsigned_integers)
)


@pytest.mark.parametrize("left, right", not_allowed_pow)
def test_not_allowed_pow(left, right):
    with pytest.raises(Exception) as invalid_operation:
        left ** right
    assert invalid_operation.type == TypeError


# List of operands that the shift operation do not accept.
not_allowed_shift = (
        combine_lists(combine_lists(booleans, booleans), shift_functions)
        + combine_lists(combine_lists(integers, booleans), shift_functions)
        + combine_lists(combine_lists(unsigned_integers, booleans), shift_functions)
        + combine_lists(combine_lists(booleans, integers), shift_functions)
        + combine_lists(combine_lists(integers, integers), shift_functions)
        + combine_lists(combine_lists(unsigned_integers, integers), shift_functions)
        + combine_lists(combine_lists(booleans, unsigned_integers), shift_functions)
        + combine_lists(combine_lists(integers, secret_unsigned_integers), shift_functions)
        + combine_lists(combine_lists(unsigned_integers, secret_unsigned_integers), shift_functions)
)


@pytest.mark.parametrize("left, right, operation", not_allowed_shift)
def test_not_allowed_shift(left, right, operation):
    with pytest.raises(Exception) as invalid_operation:
        operation(left, right)
    assert invalid_operation.type == TypeError


# List of operands that the public_equals function does not accept.
not_allowed_public_equals_operands = (combine_lists(variable_integers, variable_unsigned_integers)
                                      + combine_lists(variable_unsigned_integers, variable_integers))


@pytest.mark.parametrize("left, right", not_allowed_public_equals_operands)
def test_not_allowed_public_equals(
        left: Union["PublicInteger", "SecretInteger", "PublicUnsignedInteger", "SecretUnsignedInteger"]
        , right: Union["PublicInteger", "SecretInteger", "PublicUnsignedInteger", "SecretUnsignedInteger"]
):
    with pytest.raises(Exception) as invalid_operation:
        left.public_equals(right)
    assert invalid_operation.type == TypeError


# List of types that does not support the function invert.
not_allowed_invert_operands = integers + unsigned_integers


@pytest.mark.parametrize("operand", not_allowed_invert_operands)
def test_not_allowed_invert_operations(operand):
    with pytest.raises(Exception) as invalid_operation:
        operand.__invert__()
    assert invalid_operation.type == AttributeError


# List of operands that the probabilistic truncation does not accept.
not_allowed_trunc_pr_operands = (
        combine_lists(booleans, booleans)
        + combine_lists(integers, booleans)
        + combine_lists(unsigned_integers, booleans)
        + combine_lists(booleans, integers)
        + combine_lists(integers, integers)
        + combine_lists(unsigned_integers, integers)
        + combine_lists(booleans, unsigned_integers)
        + combine_lists(integers, secret_unsigned_integers)
        + combine_lists(public_integers, public_unsigned_integers)
        + combine_lists(unsigned_integers, secret_unsigned_integers)
        + combine_lists(public_unsigned_integers, public_unsigned_integers)
)


@pytest.mark.parametrize("left, right", not_allowed_trunc_pr_operands)
def test_not_allowed_trunc_pr(left, right):
    with pytest.raises(Exception) as invalid_operation:
        left.trunc_pr(right)
    assert invalid_operation.type == TypeError or invalid_operation.type == AttributeError


# List of types that can not generate a random value
random_operands = booleans + public_integers + public_unsigned_integers


@pytest.mark.parametrize("operand", random_operands)
def test_not_allowed_random(operand):
    with pytest.raises(Exception) as invalid_operation:
        operand.random()
    assert invalid_operation.type == AttributeError


# List of types that can not invoke the function to_public()
to_public_operands = public_booleans + public_integers + public_unsigned_integers


@pytest.mark.parametrize("operand", to_public_operands)
def test_not_to_public(operand):
    with pytest.raises(Exception) as invalid_operation:
        operand.to_public()
    assert invalid_operation.type == AttributeError


# List of operands that the function if_else does not accept
not_allowed_if_else_operands = (
        # Boolean branches
        combine_lists(booleans, combine_lists(booleans, booleans))
        # Branches with different types
        + combine_lists(booleans, combine_lists(integers, booleans))
        + combine_lists(booleans, combine_lists(unsigned_integers, booleans))
        + combine_lists(booleans, combine_lists(booleans, integers))
        + combine_lists(booleans, combine_lists(unsigned_integers, integers))
        + combine_lists(booleans, combine_lists(booleans, unsigned_integers))
        + combine_lists(booleans, combine_lists(integers, unsigned_integers))
        # The condition is a literal
        + combine_lists([Boolean(value=True)], combine_lists(integers, integers))
        + combine_lists([Boolean(value=True)], combine_lists(unsigned_integers, unsigned_integers))
)


@pytest.mark.parametrize("condition, left, right", not_allowed_if_else_operands)
def test_if_else(condition: BooleanType, left: ScalarType, right: ScalarType):
    with pytest.raises(Exception) as invalid_operation:
        condition.if_else(left, right)
    assert invalid_operation.type == TypeError
