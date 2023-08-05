class Infinity:
    """
    Class representing infinity. Supports comparsion operations.
    Instances of Infinity are greater than everything except infinities.
    """

    def __eq__(self, other):
        return isinstance(other, self.__class__) or other == float('inf')

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return self != other

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return self == other

    def __lt__(self, other):
        return False

    def __neg__(self):
        return neg_inf

    def __repr__(self):
        return 'inf'


class NegativeInfinity:
    """
    Class representing negative infinity. Supports comparsion operations.
    Its instances are less than everything except negative infinities.
    """

    def __eq__(self, other):
        return isinstance(other, self.__class__) or other == float('-inf')

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return self == other

    def __le__(self, other):
        return True

    def __lt__(self, other):
        return self != other

    def __neg__(self):
        return inf

    def __repr__(self):
        return 'neg_inf'


def is_finite(value):
    return neg_inf != value != inf


inf = Infinity()
neg_inf = NegativeInfinity()

