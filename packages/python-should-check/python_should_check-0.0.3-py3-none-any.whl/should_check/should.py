"""
@copyright: 2015 - 2018 SSH Communications Security Corporation.
@author: Pauli Rikula
@license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import enum


def be_callable(name, value):
    if value is None:
        return
    if not callable(value):
        raise ValueError("'{}' should be callable".format(name))


def be_py_enum_str(enum_type: enum.Enum):
    enum_type_keys = [e.name for e in enum_type]

    def check(name, value):
        if value is None:
            return
        if value not in enum_type_keys:
            raise TypeError("{} '{}' should be one of '{}'".format(name, value, enum_type_keys))
    return check


def be_instance_of(a_type: type):
    def check(name, value):
        if value is None:
            return
        if not isinstance(value, a_type):
            raise TypeError("{} '{}' should be instance of '{}'".format(name, value, a_type))
    return check


def be_subclass_of(a_type: type):
    def check(name, value):
        if value is None:
            return
        if not issubclass(value, a_type):
            raise TypeError("{} '{}' should be subclass of '{}'".format(name, value, a_type))
    return check


def not_be_none(name, value):
    if value is None:
        raise ValueError("'{}' should not be None".format(name))
    
        
def not_contain(item):
    def check(name, value):
        if value is None:
            return
        if item in value:
            raise ValueError("'{}' should not contain '{}'".format(name, item))
    return check


def contain(item):
    def check(name, value):
        if value is None:
            return
        if not item in value:
            raise ValueError("'{}' should contain '{}'".format(name, item))
    return check


def not_be_empty(name, value):
    if value is None:
        return
    if len(value) == 0:
        raise ValueError("'{}' should not be empty".format(name))


def not_be_negative(name, value):
    if value is None:
        return
    if value < 0:
        raise ValueError("'{}' should not be negative".format(name))
    

def be_greater_than(other):
    def check(name, value):
        if value is None:
            return
        if value <= other:
            raise ValueError("{} '{}' should be greater than '{}'".format(name, value, other))
    return check


def be_less_than(other):
    def check(name, value):
        if value is None:
            return
        if value > other:
            raise ValueError("{} '{}' should be less than '{}'".format(name, value, other))
    return check


def be_shorter_than(length):
    def check(name, value):
        if value is None:
            return
        if not len(value) <= length:
            raise ValueError("{} length '{}' should be equal or less than '{}'".format(name, len(value), length))
    return check


def be_length_of(length):
    def check(name, value):
        if value is None:
            return
        if len(value) != length:
            raise ValueError("{} length '{}' should be equal with '{}'".format(name, len(value), length))
    return check


def be_equal_with(other):
    def check(name, value):
        if value != other:
            raise ValueError("{} '{}' should be equal with '{}'".format(name, value, other))
    return check


def be(other):
    def check(name, value):
        if value is not other:
            raise ValueError("{} '{}' should (reference equally) be '{}'".format(name, value, other))
    return check


def be_in(items):
    def check(name, value):
        if value not in items:
            raise ValueError("{} '{}' should be in '{}'".format(name, value, items))
    return check