from nada_dsl import *
from lib import function


def nada_main():
    party1 = Party(name="Party1")
    my_int1 = PublicInteger(Input(name="my_int1", party=party1))
    my_int2 = PublicInteger(Input(name="my_int2", party=party1))

    addition = my_int1 * my_int2
    equals = my_int1 == my_int2
    pow = my_int1**my_int2
    sum_list = sum([my_int1, my_int2])
    shift_l = my_int1 << UnsignedInteger(2)
    shift_r = my_int1 >> UnsignedInteger(2)
    function_result = function(my_int1, my_int2)

    return [
        Output(addition, "addition", party1),
        Output(equals, "equals", party1),
        Output(pow, "pow", party1),
        Output(sum_list, "sum_list", party1),
        Output(shift_l, "shift_l", party1),
        Output(shift_r, "shift_r", party1),
        Output(function_result, "function_result", party1),
    ]
