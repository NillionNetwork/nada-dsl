"""
Nada DSL audit component tests.
"""
import richreports

from nada_dsl.audit.strict import strict

def test_strict_syntax():
    source = """
from nada_dsl import *

def nada_main():
    party1 = Party(name="Party1")
    my_int1 = PublicInteger(Input(name="my_int1", party=party1))
    my_int2 = SecretInteger(Input(name="my_int2", party=party1))

    b = True and(False)or not True and False
    d = not(123) and not False
    b = True and   123 or True
    b = (True and(
          False
       )  or
       not True and False)
    c = 123>456
    c = 123 > 456
    c = True > 456
    c = 123 == '123'
    c = 'abc' == 'abc'
    d = 1 < 2 < 3 < 4
    e = 123 - 324
    e = 123 + 324
    e = 123 * 324
    e = my_int2 - my_int1
    e = my_int2 + my_int1
    e = my_int2 * my_int1
    (x, y, z) = (1, 2, 3)

    x: int = 123
    x: bool = 132

    l = []
    l: list[int] = []
    l: list = []
    l = [1, 2, 3]
    l: list[int] = [1, 2, 3]
    l: list[int] = ['abc', 2, 3]
    l: list[list[int]] = []
    l: list[list[int]] = [[1], [2], [3]]
    l[0] = [4]
    
    l.append('abc')
    l.append(4)
    l.append([4])

    new_int = my_int1 * my_int2

    return [Output(value=new_int, party=party1, name="my_output")]
"""
    assert(isinstance(strict(source), richreports.report))

def test_strict_functional():
    source = """
from nada_dsl import *

def nada_main():
    voters = [Party("Party" + str(v)) for v in range(2)]
    outparty = Party(name="OutParty")

    votes_per_candidate = [
        [
            SecretInteger(
                Input(
                    name="v" + str(v) + "_c" + str(c),
                    party=Party("Party" + str(v))
                )
            )
            for v in range(2)
        ]
        for c in range(4)
    ]

    return [
      Output(sum(votes_per_candidate[c]), "c" + str(c), outparty)
      for c in range(4)
    ]
"""
    assert(isinstance(strict(source), richreports.report))

def test_strict_imperative():
    source = """
from nada_dsl import *
# In this example, note that empty lists must be accompanied by an explicit
# type annotation.

from nada_dsl import *

def nada_main():

    # Create the voter parties and recipient party.
    voters: list[Party] = []
    for v in range(2):
        voters.append(Party("Party" + str(v)))
    outparty = Party(name="OutParty")

    # Gather the inputs (one vote for each candidate from each voter).
    votes_per_candidate: list[list[SecretInteger]] = []
    for c in range(4):
        votes_per_candidate.append([])
        for v in range(2):
            votes_per_candidate[c].append(SecretInteger(
                Input(
                    name="v" + str(v) + "_c" + str(c),
                    party=Party("Party" + str(v))
                )
            ))

    # Calculate the total for each candidate.
    outputs: list[Output] = []
    for c in range(4):
        outputs.append(Output(sum(votes_per_candidate[c]), "c" + str(c), outparty))

    return outputs
"""
    assert(isinstance(strict(source), richreports.report))
