"""
Nada DSL Exceptions.
"""


class NotAllowedException(Exception):
    """Exception for not allowed use cases."""


class InvalidTypeError(Exception):
    """Invalid type error"""


class MissingProgramArgumentError(Exception):
    """Missing program argument"""


class MissingEntryPointError(Exception):
    """Missing nada_main entry point for the program."""


class IncompatibleTypesError(Exception):
    """The types in an operation are not compatible."""
