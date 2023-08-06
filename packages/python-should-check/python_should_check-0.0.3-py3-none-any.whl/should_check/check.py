"""
@copyright: 2015 - 2018 SSH Communications Security Corporation.
@author: Pauli Rikula
@license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""


class Check(object):
    """Check parameters and raise comprehensible exceptions.

    >>> from should_check import (
    ...    Check,
    ...    be_callable,
    ...    be_py_enum_str,
    ...    be_instance_of,
    ...    be_subclass_of,
    ...    not_be_none,
    ...    not_contain,
    ...    contain,
    ...    not_be_empty,
    ...    be_shorter_than,
    ...    be_length_of,
    ...    not_be_negative,
    ...    be_greater_than,
    ...    be_less_than,
    ...    be_equal_with,
    ...    be,
    ...    be_in)


## Check if a function is a callable and not None

    >>> function = Check(function=print).should(not_be_none, be_callable)
    >>> function("Hello world")
    Hello world

    >>> function = Check(function=None).should(not_be_none, be_callable)
    Traceback (most recent call last):
    ...
    ValueError: 'function' should not be None

    >>> function = Check(function="boo").should(not_be_none, be_callable)
    Traceback (most recent call last):
    ...
    ValueError: 'function' should be callable


If the 'None' would not go through some of these checks, it would be cumbersome to
check optional parameters on your functions. This for example works:


    >>> function = Check(function=None).should(be_callable)


But these wont:


    >>> checked = Check(value=None).should(be(1))
    Traceback (most recent call last):
    ...
    ValueError: value 'None' should (reference equally) be '1'

    >>> checked = Check(value=None).should(be_in([1,2]))
    Traceback (most recent call last):
    ...
    ValueError: value 'None' should be in '[1, 2]'

    >>> checked = Check(value=None).should(be_equal_with(1))
    Traceback (most recent call last):
    ...
    ValueError: value 'None' should be equal with '1'


So be carefull with None and add the check everywhere like you should anyway.

## Check if a string is a member of an enum definition


    >>> import enum
    >>> class MyEnum(enum.IntEnum):
    ...   GOOD_ENUM = 0
    ...   MEH_ENUM = 1
    ...
    >>> enum_str = Check(enum_str="GOOD_ENUM").should(not_be_none, be_py_enum_str(MyEnum))
    >>> enum_str = Check(enum_str="BAD_ENUM").should(not_be_none, be_py_enum_str(MyEnum))
    Traceback (most recent call last):
    ...
    TypeError: enum_str 'BAD_ENUM' should be one of '['GOOD_ENUM', 'MEH_ENUM']'


## Check if an object is an instance of a class


    >>> my_enum = MyEnum(0)
    >>> second_enum = Check(my_enum=my_enum).should(not_be_none, be_instance_of(MyEnum))
    >>> second_enum =  Check(my_enum=my_enum).should(not_be_none, be_instance_of(int))
    >>> second_enum =  Check(my_enum=my_enum).should(not_be_none, be_instance_of(str))
    Traceback (most recent call last):
    ...
    TypeError: my_enum '0' should be instance of '<class 'str'>'

## Check if a class is a subclass another


    >>> CheckedClass = Check(subclass=MyEnum).should(
    ...    not_be_none,
    ...    be_subclass_of(enum.IntEnum),
    ...    be_subclass_of(int),
    ...    be_subclass_of(str))
    Traceback (most recent call last):
    ...
    TypeError: subclass '<enum 'MyEnum'>' should be subclass of '<class 'str'>'


## Check that an item is not in container


    >>> checked_item = Check(item=[1,2,3]).should(not_be_none, not_contain(51))
    >>> checked_item = Check(item=[1,2,3]).should(not_be_none, not_contain(1))
    Traceback (most recent call last):
    ...
    ValueError: 'item' should not contain '1'


## Check that an item is in a container


    >>> checked_item = Check(item=[1,2,3]).should(not_be_none, contain(1))
    >>> checked_item = Check(item=[1,2,3]).should(not_be_none, contain(51))
    Traceback (most recent call last):
    ...
    ValueError: 'item' should contain '51'


## Check that a collection is not empty


    >>> not_empty = Check(collection=[1,2,3]).should(not_be_none, not_be_empty)
    >>> not_empty = Check(collection=set()).should(not_be_none, not_be_empty)
    Traceback (most recent call last):
    ...
    ValueError: 'collection' should not be empty


## Length checks for containers (strings)


    >>> capped = Check(number="a").should(not_be_none, be_shorter_than(2))
    >>> capped = Check(number="aaa").should(not_be_none, be_shorter_than(2))
    Traceback (most recent call last):
    ...
    ValueError: number length '3' should be equal or less than '2'

    >>> fixed = Check(number="aa").should(not_be_none, be_length_of(2))
    >>> fixed = Check(number="aaa").should(not_be_none, be_length_of(2))
    Traceback (most recent call last):
    ...
    ValueError: number length '3' should be equal with '2'


## Range checks for numbers:

    >>> positive = Check(number=-1).should(not_be_none, not_be_negative)
    Traceback (most recent call last):
    ...
    ValueError: 'number' should not be negative

    >>> positive = Check(number=-1).should(not_be_none, be_greater_than(0))
    Traceback (most recent call last):
    ...
    ValueError: number '-1' should be greater than '0'

    >>> positive = Check(number=4).should(not_be_none, be_less_than(1))
    Traceback (most recent call last):
    ...
    ValueError: number '4' should be less than '1'


## Equality checks


    >>> equals_one = Check(number="1").should(not_be_none, be_equal_with("1"))
    >>> equals_one = Check(number="2").should(not_be_none, be_equal_with("1"))
    Traceback (most recent call last):
    ...
    ValueError: number '2' should be equal with '1'

    >>> reference = object()
    >>> equals_one = Check(object=reference).should(not_be_none, be(reference))
    >>> equals_one = Check(object="another").should(be(None))
    Traceback (most recent call last):
    ...
    ValueError: object 'another' should (reference equally) be 'None'

    """
    def __init__(self, **args):
        self.args = args

    def should(self, *checks):
        """
        Argument dictionary keys are used to set the property values on
        the possibly generated exceptions.
        Returns one of the handled values.
        """
        value = None
        for name, value in self.args.items():
            for check in checks:
                check(name, value)
        return value

    def property(self, property_name):
        """
        Replaces the original value with the values property value on the checks.
        Returns the modified object (self).
        """
        for name, value in self.args.items():
            if value is not None:
                self.args[name] = getattr(value, property_name)
        return self


if __name__ == '__main__':
    import doctest


    doctest.testmod()
