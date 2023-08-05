from set_algebra.endpoint import Endpoint
from set_algebra.parser import OPEN_LEFT_TO_BOUNDS_MAPPING, string_types


class Interval(object):
    """
    Class representing interval on an axis.
    Contains two Endpoint instances - a and b.

    There are 3 ways to instantiate Interval:
    - From notation string (for numeric values only):
        Interval('[0, 1]')
        Interval('(3.4e+7, 5.6e+7]')
        Interval('[0, inf]')

    - From two values and bounds string:
        Interval(1, 2, '[)')

    - From two endpoints:
        a = Endpoint('[0')
        b = Endpoint('1]');
        Interval(Endpoint('[0'), Endpoint('1]'))

    Left and right values must be comparable to each other.

    Instances of Interval support membership test ("in") operation for scalars,
        Endpoint instances and other Interval instances.

    See tests/test_interval.py

    >>> real = Interval('(-inf, inf)')
    >>> 99999999 in real
    True
    >>> percentage = Interval('[0, 100]')
    >>> 50 in percentage
    True
    >>> 200 in percentage
    False
    >>> negative = Interval('(-inf, 0)')
    >>> negative
    Interval('(-inf, 0)')
    >>> 0 in negative
    False
    >>> -1 in negative
    True
    >>> negative in real
    True
    >>> percentage in negative
    False
    >>> negative in percentage
    False
    >>>
    >>> digits = Interval('0', '9', '[]')
    >>> '5' in digits
    True
    >>> a = Endpoint('p', '[')
    >>> b = Endpoint('q', ')')
    >>> p = Interval(a, b)
    >>> 'o' in p
    False
    >>> 'p' in p
    True
    >>> 'p' * 1000 in p
    True
    >>> 'q' in p
    False
    >>>
    """
    __slots__ = ('a', 'b')

    def __init__(self, notation_or_a, b=None, bounds=None):
        if b is None:
            # Init from notation.
            if bounds is not None:
                raise TypeError('bounds are only accepted with both "notation_or_a" and "b"')
            notation = notation_or_a.strip()
            a_str, b_str = notation.split(',')
            if ',' in b_str:
                raise ValueError('There should be one and only one comma in interval notation')
            a = Endpoint(a_str)
            b = Endpoint(b_str)

        else:
            if isinstance(notation_or_a, Endpoint) ^ isinstance(b, Endpoint):
                raise TypeError('Either both notation_or_a and b must be instances of Endpoint'
                                ' or none of them')

            if isinstance(b, Endpoint):
                # Init from two Endpoints.
                if bounds is not None:
                    raise TypeError('When initializing Interval from two Endpoints,'
                                    ' bounds must not be provided')
                a = notation_or_a

            else:
                # Init from two values and bounds.
                if bounds is None:
                    raise TypeError('When initializing Interval from two values, '
                                    'bounds must be provided')
                value_a = notation_or_a
                value_b = b
                if not isinstance(bounds, string_types):
                    raise TypeError('bounds must be a string, not %s' % type(bounds).__name__)
                if len(bounds) != 2:
                    raise ValueError('bounds must be a string of length 2, e.g. "[)"')
                a = Endpoint(value_a, bounds[0])
                b = Endpoint(value_b, bounds[1])

        if a.right:
            raise ValueError('First endpoint ("a") must be left')
        if b.left:
            raise ValueError('Second endpoint ("b") must be right')
        if a > b:
            raise ValueError('First endpoint ("a") must be less than the second one')
        # a == b Allowed for degenerate interval.

        self.a = a
        self.b = b

    @property
    def notation(self):
        return '%s, %s' % (self.a.notation, self.b.notation)

    def __repr__(self):
        classname = type(self).__name__
        if isinstance(self.a.value, Endpoint.PARSABLE_TYPES):
            return "%s('%s')" % (classname, self.notation)
        else:
            a = self.a
            b = self.b
            bound_a = OPEN_LEFT_TO_BOUNDS_MAPPING[a.open, a.left]
            bound_b = OPEN_LEFT_TO_BOUNDS_MAPPING[b.open, b.left]
            bounds = bound_a + bound_b
            return "%s(%s, %s, '%s')" % (classname, repr(a.value), repr(b.value), bounds)

    def __eq__(self, other):
        return isinstance(other, Interval) \
           and self.a == other.a and self.b == other.b

    def __contains__(self, other):
        if isinstance(other, Interval):
            return self.a <= other.a and other.b <= self.b
        else:
            return self.a <= other and self.b >= other

    def copy(self):
        """
        Return a shallow copy of the Interval.
        Endpoints are recreated.
        copy is safe as long as endpoint values are of immutable types.
        """
        return Interval(self.a.copy(), self.b.copy())


def is_interval(obj):
    return isinstance(obj, Interval)


def is_scalar(obj):
    return not isinstance(obj, Interval)


# unbounded represents interval from -inf to inf
unbounded = Interval('(-inf, inf)')

