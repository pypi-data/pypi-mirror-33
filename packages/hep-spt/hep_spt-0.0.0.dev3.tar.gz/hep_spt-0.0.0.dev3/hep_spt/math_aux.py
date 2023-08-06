'''
Auxiliar mathematical functions.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Custom
from hep_spt.core import taking_ndarray
from hep_spt.cpython import math_aux_cpy

# Python
import numpy as np
from functools import reduce


__all__ = ['bit_length', 'gcd', 'ibinary_repr', 'is_power_2', 'lcm', 'next_power_2']


def bit_length( arg ):
    '''
    Get the length of the binary representation of the given value(s).
    This function is equivalent to :func:`int.bit_length`, but can take arrays
    as an input.

    :param arg: array of values.
    :type arg: int or numpy.ndarray(int)
    :returns: length of the binary representation.
    :rtype: numpy.ndarray(int)
    :raises TypeError: If the input does not contain integer values.
    '''
    return math_aux_cpy.bit_length(arg)


def gcd( a, b, *args ):
    '''
    Calculate the greatest common divisor of a set of numbers.

    :param a: first number(s).
    :type a: int or numpy.ndarray(int)
    :param b: second number(s).
    :type b: int or numpy.ndarray(int)
    :param args: any other numbers.
    :type args: tuple(int or numpy.ndarray(int))
    :returns: Greatest common divisor of a set of numbers.
    :rtype: int or numpy.ndarray(int)
    :raises TyperError: If the arrays do not contain integers or if \
    the shapes do not coincide.
    '''
    if len(args) == 0:
        return math_aux_cpy.gcd(a, b)
    else:
        return reduce(math_aux_cpy.gcd, args + (a, b))


def ibinary_repr( arg ):
    '''
    Get the binary representation of the given value(s).
    This function is equivalent to :func:`numpy.binary_repr`, but the returned
    value is an integer.

    :param arg: array of values.
    :type arg: int or numpy.ndarray(int)
    :returns: Values in binary representation (as integers).
    :rtype: numpy.ndarray(int)
    :raises TypeError: If the input does not contain integer values.
    '''
    return math_aux_cpy.ibinary_repr(arg)


@taking_ndarray
def is_power_2( arg ):
    '''
    Determine whether the input number(s) is a power of 2 or not. Only
    works with positive numbers.

    :param arg: input number(s).
    :type arg: int or numpy.ndarray(int)
    :returns: Whether the input number(s) is(are) a power of 2 or not.
    :rtype: bool or numpy.ndarray(bool)
    '''
    return np.logical_and(arg > 0, ((arg & (arg - 1)) == 0))


@taking_ndarray
def lcm( a, b, *args ):
    '''
    Calculate the least common multiple of a set of numbers.

    :param a: first number(s).
    :type a: int or numpy.ndarray(int)
    :param b: second number(s).
    :type b: int or numpy.ndarray(int)
    :param args: any other numbers.
    :type args: tuple(int or numpy.ndarray(int))
    :returns: Least common multiple of a set of numbers.
    :rtype: int or numpy.ndarray(int)
    '''
    if len(args) == 0:
        return a*b//gcd(a, b)
    else:
        return reduce(lcm, args + (a, b))


@taking_ndarray
def next_power_2( arg ):
    '''
    Calculate the next number(s) greater than that(those) given and being a power(s) of 2.

    :param arg: input number(s).
    :type arg: int or numpy.ndarray(int)
    :returns: Next power of 2 to the given number.
    :rtype: int or numpy.ndarray(int)

    .. note: If the input number is a power of two, it will return the \
    same number.
    '''
    return 1 << bit_length(arg - 1)
