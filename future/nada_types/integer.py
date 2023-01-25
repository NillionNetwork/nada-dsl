from dataclasses import dataclass
from typing import Union, Type

from nada_dsl import SourceRef
from nada_dsl.nada_types import NadaType
from nada_dsl.future.operations import Cast
from nada_dsl.operations import Addition, Multiplication
from nada_dsl.nada_types.integer import SecretBigInteger


@dataclass
class PublicInteger8(NadaType):

    def __add__(self, other: Union['PublicInteger8', 'SecretInteger8']) -> Union['PublicInteger8', 'SecretInteger8']:
        addition = Addition(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger8:
            return PublicInteger8(inner=addition)
        elif type(other) == SecretInteger8:
            return SecretInteger8(inner=addition)
        else:
            raise Exception(f"Cannot add {self} + {other}")

    def __mul__(self, other: Union['PublicInteger8', 'SecretInteger8']) -> Union['PublicInteger8', 'SecretInteger8']:
        multiplication = Multiplication(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger8:
            return PublicInteger8(inner=multiplication)
        elif type(other) == SecretInteger8:
            return SecretInteger8(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")

    def cast(self, to: Union[Type['PublicInteger16']]) -> 'PublicInteger16':
        return PublicInteger16(inner=Cast(target=self, to=to, source_ref=SourceRef.back_frame()))


@dataclass
class PublicInteger16(NadaType):

    def __add__(self, other: Union['PublicInteger16', 'SecretInteger16']) -> Union[
        'PublicInteger16', 'SecretInteger16']:
        addition = Addition(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger16:
            return PublicInteger16(inner=addition)
        elif type(other) == SecretInteger16:
            return SecretInteger16(inner=addition)
        else:
            raise Exception(f"Cannot add {self} + {other}")

    def __mul__(self, other: Union['PublicInteger16', 'SecretInteger16']) -> Union[
        'PublicInteger16', 'SecretInteger16']:
        multiplication = Multiplication(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger16:
            return PublicInteger16(inner=multiplication)
        elif type(other) == SecretInteger16:
            return SecretInteger16(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")


@dataclass
class PublicBigInteger(NadaType):
    def __add__(self, other: Union['PublicBigInteger', 'SecretBigInteger']) -> Union[
        'PublicBigInteger', 'SecretBigInteger']:
        addition = Addition(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicBigInteger:
            return PublicBigInteger(inner=addition)
        elif type(other) == SecretBigInteger:
            return SecretBigInteger(inner=addition)
        else:
            raise Exception(f"Cannot add {self} + {other}")

    def __mul__(self, other: Union['PublicBigInteger', 'SecretBigInteger']) -> Union[
        'PublicBigInteger', 'SecretBigInteger']:
        multiplication = Multiplication(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicBigInteger:
            return PublicBigInteger(inner=multiplication)
        elif type(other) == SecretInteger16:
            return SecretBigInteger(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")


@dataclass
class SecretInteger8(NadaType):
    def __add__(self, other: Union['PublicInteger8', 'SecretInteger8']) -> Union['SecretInteger8']:
        addition = Addition(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger8 or type(other) == SecretInteger8:
            return SecretInteger8(inner=addition)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: Union['PublicInteger8', 'SecretInteger8']) -> Union['SecretInteger8']:
        multiplication = Multiplication(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger8 or type(other) == SecretInteger8:
            return SecretInteger8(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")

    def cast(self, to: Union[Type['SecretInteger16']]) -> 'SecretInteger16':
        return SecretInteger16(inner=Cast(target=self, to=to, source_ref=SourceRef.back_frame()))


@dataclass
class SecretInteger16(NadaType):
    def __add__(self, other: Union['PublicInteger16', 'SecretInteger16']) -> Union['SecretInteger16']:
        addition = Addition(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger16 or type(other) == SecretInteger16:
            return SecretInteger16(inner=addition)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: Union['PublicInteger16', 'SecretInteger16']) -> Union['SecretInteger16']:
        multiplication = Multiplication(right=self, left=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicInteger16 or type(other) == SecretInteger16:
            return SecretInteger16(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")
