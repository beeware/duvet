"""
This module is for testing duvet.
The intended usage is that this code is tested with unittests in such a way
that the coverage can be known in advance.  It is then compared with the coverage
reported by duvet.

It is also useful for duvet to have something to chew on while under development.
"""


def fully_covered_add(a, b):
    """
    Every line in this function should be covered by a simple test
    """
    answer = a + b
    return answer


def non_fully_covered_add(a, b, condition=False):
    """
    The difference line in this function will only be executed if condition is True.
    """
    if condition:
        diff = a - b
    answer = a + b
    return answer
