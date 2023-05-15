from dataclasses import dataclass
from typing import Union, Type

from nada_dsl import SourceRef
from nada_dsl.nada_types import NadaType
from nada_dsl.future.operations import Cast
from nada_dsl.operations import Addition, Multiplication, CompareLessThan
from nada_dsl.nada_types.unsigned_integer import SecretBigUnsignedInteger
from nada_dsl.nada_types.boolean import SecretBoolean


@dataclass
class PublicUnsignedInteger8(NadaType):
    def __add__(
        self, other: Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]
    ) -> Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]:
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger8):
            return PublicUnsignedInteger8(inner=addition)
        elif isinstance(other, SecretUnsignedInteger8):
            return SecretUnsignedInteger8(inner=addition)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(
        self, other: Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]
    ) -> Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]:
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger8):
            return PublicUnsignedInteger8(inner=multiplication)
        elif isinstance(other, SecretUnsignedInteger8):
            return SecretUnsignedInteger8(inner=multiplication)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def cast(self, to: Type["PublicUnsignedInteger16"]) -> "PublicUnsignedInteger16":
        return PublicUnsignedInteger16(
            inner=Cast(target=self, to=to, source_ref=SourceRef.back_frame())
        )

    def __lt__(
        self, other: Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]
    ) -> "SecretBoolean":
        if type(other) in [PublicUnsignedInteger8, SecretUnsignedInteger8]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")


@dataclass
class PublicUnsignedInteger16(NadaType):
    def __add__(
        self, other: Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]
    ) -> Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]:
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger16):
            return PublicUnsignedInteger16(inner=addition)
        elif isinstance(other, SecretUnsignedInteger16):
            return SecretUnsignedInteger16(inner=addition)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(
        self, other: Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]
    ) -> Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]:
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger16):
            return PublicUnsignedInteger16(inner=multiplication)
        elif isinstance(other, SecretUnsignedInteger16):
            return SecretUnsignedInteger16(inner=multiplication)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(
        self, other: Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]
    ) -> "SecretBoolean":
        if type(other) in [PublicUnsignedInteger16, SecretUnsignedInteger16]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")


@dataclass
class PublicBigUnsignedInteger(NadaType):
    def __add__(
        self, other: Union["PublicBigUnsignedInteger", "SecretBigUnsignedInteger"]
    ) -> Union["PublicBigUnsignedInteger", "SecretBigUnsignedInteger"]:
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=addition)
        elif isinstance(other, SecretBigUnsignedInteger):
            return SecretBigUnsignedInteger(inner=addition)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(
        self, other: Union["PublicBigUnsignedInteger", "SecretBigUnsignedInteger"]
    ) -> Union["PublicBigUnsignedInteger", "SecretBigUnsignedInteger"]:
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=multiplication)
        elif isinstance(other, SecretUnsignedInteger16):
            return SecretBigUnsignedInteger(inner=multiplication)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")


@dataclass
class SecretUnsignedInteger8(NadaType):
    def __add__(
        self, other: Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]
    ) -> "SecretUnsignedInteger8":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger8) or isinstance(
            other, SecretUnsignedInteger8
        ):
            return SecretUnsignedInteger8(inner=addition)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(
        self, other: Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]
    ) -> "SecretUnsignedInteger8":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger8) or isinstance(
            other, SecretUnsignedInteger8
        ):
            return SecretUnsignedInteger8(inner=multiplication)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def cast(self, to: Type["SecretUnsignedInteger16"]) -> "SecretUnsignedInteger16":
        return SecretUnsignedInteger16(
            inner=Cast(target=self, to=to, source_ref=SourceRef.back_frame())
        )

    def __lt__(
        self, other: Union["PublicUnsignedInteger8", "SecretUnsignedInteger8"]
    ) -> "SecretBoolean":
        if type(other) in [PublicUnsignedInteger8, SecretUnsignedInteger8]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")


@dataclass
class SecretUnsignedInteger16(NadaType):
    def __add__(
        self, other: Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]
    ) -> "SecretUnsignedInteger16":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger16) or isinstance(
            other, SecretUnsignedInteger16
        ):
            return SecretUnsignedInteger16(inner=addition)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(
        self, other: Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]
    ) -> "SecretUnsignedInteger16":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger16) or isinstance(
            other, SecretUnsignedInteger16
        ):
            return SecretUnsignedInteger16(inner=multiplication)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(
        self, other: Union["PublicUnsignedInteger16", "SecretUnsignedInteger16"]
    ) -> "SecretBoolean":
        if type(other) in [PublicUnsignedInteger16, SecretUnsignedInteger16]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")
