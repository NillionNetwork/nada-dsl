from dataclasses import dataclass
from typing import Union, Type

from nada_dsl import SourceRef
from nada_dsl.nada_types import NadaType
from nada_dsl.future.operations import Cast
from nada_dsl.operations import Addition, Multiplication, CompareLessThan
from nada_dsl.nada_types.integer import SecretBigInteger
from nada_dsl.nada_types.boolean import SecretBoolean


@dataclass
class PublicInteger8(NadaType):
    def __add__(
        self, other: Union["PublicInteger8", "SecretInteger8"]
    ) -> Union["PublicInteger8", "SecretInteger8"]:
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger8):
            return PublicInteger8(inner=addition)
        elif isinstance(other, SecretInteger8):
            return SecretInteger8(inner=addition)
        else:
            raise TypeError(f"Cannot add {self} + {other}")

    def __mul__(
        self, other: Union["PublicInteger8", "SecretInteger8"]
    ) -> Union["PublicInteger8", "SecretInteger8"]:
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger8):
            return PublicInteger8(inner=multiplication)
        elif isinstance(other, SecretInteger8):
            return SecretInteger8(inner=multiplication)
        else:
            raise TypeError(f"Cannot multiply {self} * {other}")

    def cast(self, to: Type["PublicInteger16"]) -> "PublicInteger16":
        return PublicInteger16(
            inner=Cast(target=self, to=to, source_ref=SourceRef.back_frame())
        )

    def __lt__(
        self, other: Union["PublicInteger8", "SecretInteger8"]
    ) -> "SecretBoolean":
        if type(other) in [PublicInteger8, SecretInteger8]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Cannot compare {self} with {other}")


@dataclass
class PublicInteger16(NadaType):
    def __add__(
        self, other: Union["PublicInteger16", "SecretInteger16"]
    ) -> Union["PublicInteger16", "SecretInteger16"]:
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger16):
            return PublicInteger16(inner=addition)
        elif isinstance(other, SecretInteger16):
            return SecretInteger16(inner=addition)
        else:
            raise TypeError(f"Cannot add {self} + {other}")

    def __mul__(
        self, other: Union["PublicInteger16", "SecretInteger16"]
    ) -> Union["PublicInteger16", "SecretInteger16"]:
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger16):
            return PublicInteger16(inner=multiplication)
        elif isinstance(other, SecretInteger16):
            return SecretInteger16(inner=multiplication)
        else:
            raise TypeError(f"Cannot multiply {self} * {other}")

    def __lt__(
        self, other: Union["PublicInteger16", "SecretInteger16"]
    ) -> "SecretBoolean":
        if type(other) in [PublicInteger16, SecretInteger16]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Cannot compare {self} with {other}")


@dataclass
class PublicBigInteger(NadaType):
    def __add__(
        self, other: Union["PublicBigInteger", "SecretBigInteger"]
    ) -> Union["PublicBigInteger", "SecretBigInteger"]:
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=addition)
        elif isinstance(other, SecretBigInteger):
            return SecretBigInteger(inner=addition)
        else:
            raise TypeError(f"Cannot add {self} + {other}")

    def __mul__(
        self, other: Union["PublicBigInteger", "SecretBigInteger"]
    ) -> Union["PublicBigInteger", "SecretBigInteger"]:
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=multiplication)
        elif isinstance(other, SecretInteger16):
            return SecretBigInteger(inner=multiplication)
        else:
            raise TypeError(f"Cannot multiply {self} * {other}")


@dataclass
class SecretInteger8(NadaType):
    def __add__(
        self, other: Union["PublicInteger8", "SecretInteger8"]
    ) -> "SecretInteger8":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger8) or isinstance(other, SecretInteger8):
            return SecretInteger8(inner=addition)
        else:
            raise TypeError(f"Cannot add {self} {other}")

    def __mul__(
        self, other: Union["PublicInteger8", "SecretInteger8"]
    ) -> "SecretInteger8":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger8) or isinstance(other, SecretInteger8):
            return SecretInteger8(inner=multiplication)
        else:
            raise TypeError(f"Cannot multiply {self} * {other}")

    def cast(self, to: Type["SecretInteger16"]) -> "SecretInteger16":
        return SecretInteger16(
            inner=Cast(target=self, to=to, source_ref=SourceRef.back_frame())
        )

    def __lt__(
        self, other: Union["PublicInteger8", "SecretInteger8"]
    ) -> "SecretBoolean":
        if type(other) in [PublicInteger8, SecretInteger8]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Cannot compare {self} with {other}")


@dataclass
class SecretInteger16(NadaType):
    def __add__(
        self, other: Union["PublicInteger16", "SecretInteger16"]
    ) -> "SecretInteger16":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger16) or isinstance(other, SecretInteger16):
            return SecretInteger16(inner=addition)
        else:
            raise TypeError(f"Cannot add {self} {other}")

    def __mul__(
        self, other: Union["PublicInteger16", "SecretInteger16"]
    ) -> "SecretInteger16":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger16) or isinstance(other, SecretInteger16):
            return SecretInteger16(inner=multiplication)
        else:
            raise TypeError(f"Cannot multiply {self} * {other}")

    def __lt__(
        self, other: Union["PublicInteger16", "SecretInteger16"]
    ) -> "SecretBoolean":
        if type(other) in [PublicInteger16, SecretInteger16]:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Cannot compare {self} with {other}")
