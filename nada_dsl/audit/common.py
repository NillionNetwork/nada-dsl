"""
Common classes and functions for the Nada DSL auditing component
(used across different static analysis submodules).
"""
# pylint: disable=wildcard-import,invalid-name
# pylint: disable=too-few-public-methods
from __future__ import annotations
import ast

class Rule(Exception):
    """
    Base class for violations of rules defined by static analysis submodules.
    """

class RuleInAncestor:
    """
    Rule attribute value that indicates that the Nada DSL rule attribute of an
    :obj:`ast` node is determined by an ancestor node's Nada DSL rule attribute.
    """

class SyntaxRestriction(Rule):
    """
    Base class for violations of syntax restrictions defined by static analysis
    submodules.
    """

class TypeErrorRoot(TypeError):
    """
    Class for type errors that are not caused by other type errors.
    """

class TypeInParent:
    """
    Type attribute value that indicates that the Nada DSL type attribute of an
    :obj:`ast` node is determined by the parent node's Nada DSL type attribute.
    """

class Feedback:
    """
    Feedback aggregator (used throughout the recursive static analysis
    algorithms in order to collect all created exceptions).
    """
    def __init__(self: Feedback):
        self.exceptions = []

    def __call__(self: Feedback, exception: Exception):
        self.exceptions.append(exception)
        return exception

def typeerror_demote(t):
    """
    Demote a direct-cause type error to a generic (possibly indirect) type error.
    """
    if isinstance(t, TypeErrorRoot):
        return TypeError(str(t))

    return t

def audits(node, key, value=None, default=None, delete=False):
    """
    Set, update, or delete an :obj:`ast` node's static analysis attribute.
    """
    # pylint: disable=protected-access
    if not hasattr(node, '_audits'):
        setattr(node, '_audits', {})

    if value is None:
        value = node._audits.get(key, default)
        if delete and key in node._audits:
            del node._audits[key]
        return value

    node._audits[key] = value

    return None

def rules_no_restriction(a, recursive=False):
    """
    Delete the rule attributes of an :obj:`ast` node (and possibly those of its
    descendants).
    """
    if recursive:
        for a_ in ast.walk(a):
            audits(a_, 'rules', delete=True)
    else:
        audits(a, 'rules', delete=True)

def unify(t_a, t_b):
    """
    Perform basic type unification of Python types.
    """
    if t_a == t_b:
        return t_a

    if t_a.__name__ == 'list' and t_b.__name__ == 'list':
        if hasattr(t_a, '__args__') and len(t_a.__args__) == 1:
            if hasattr(t_b, '__args__'):
                if len(t_b.__args__) == 1:
                    return unify(t_a.__args__[0], t_b.__args__[0])
                return None
            return t_a

    return None
