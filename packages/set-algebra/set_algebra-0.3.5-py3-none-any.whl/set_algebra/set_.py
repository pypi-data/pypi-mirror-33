import functools

from set_algebra.infinity import is_finite, inf, neg_inf
from set_algebra.endpoint import Endpoint, are_bounding
from set_algebra.interval import Interval, is_interval, unbounded
from set_algebra.parser import parse_value, parse_endpoint_notation, string_types


def _assert_pieces_are_ascending(fn):
    """
    Debug decorator for Set methods.
    Makes sure pieces are sorted in ascending order and do not intersect.
    """
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        res = fn(self, *args, **kwargs)
        error = None
        for i, cur in enumerate(self.pieces[:-1]):
            nex = self.pieces[i+1]
            if isinstance(cur, Interval):
                if isinstance(nex, Interval):
                    if cur.b >= nex.a:
                        error = '%s >= %s in Set %s'
                        params = (cur.b.notation, nex.a.notation, self.notation)
                    elif are_bounding(cur.b, nex.a):
                        error = 'no gap between %s and %s! in Set %s'
                        params = (cur.b.notation, nex.a.notation, self.notation)
                else:
                    if cur.b >= nex:
                        error = '%s >= %s in Set %s'
                        params = (cur, nex.a.notation, self.notation)
                    elif cur.b.value == nex:
                        error = 'no gap between %s and %s! in Set %s'
                        params = (cur.b.notation, nex, self.notation)
            else:
                if isinstance(nex, Interval):
                    if cur >= nex.a:
                        error = '%s >= %s in Set %s'
                        params = (cur, nex.a.notation, self.notation)
                    elif cur == nex.a.value:
                        error = 'no gap between %s and %s! in Set %s'
                        params = (cur, nex.a.notation, self.notation)
                else:
                    if cur >= nex:
                        error = '%s >= %s in Set %s'
                        params = (cur, nex, self.notation)
            if error:
                assert False, error % params
        return res
    return wrapper


def _copy_pieces(pieces):
    return [p.copy() if is_interval(p) else p for p in pieces]


class Set(object):
    """
    Uncountable Infinite Set

    Set can be instantiated from either:
        - iterable of intervals or scalars:
            Set([Interval('[1, 2]'), Interval('[5, inf)')])
            Set([Interval('1, 2'), 0, Interval('[6, 7]')])
        - notation string: Set('[1, 2], {3}, [5, inf)'). Note that in this case all
            the pieces must be sorted in ascending order and must not intersect.
        - another Set. Intervals will be copied.
        - nothing for empty Set: Set()
    
    The subset and equality comparisons do not generalize to a total ordering function.
    For example, any two nonempty disjoint Sets are not equal and are not subsets of each other,
    so all of the following return False: a < b, a == b, or a > b.

    Note, the non-operator versions of union(), intersection(), intersection_update(), difference(), difference_update(), symmetric_difference(), symmetric_difference_update(), issubset() and issuperset() methods will accept iterable of scalars and/or intervals as an argument.
    In contrast, their operator based counterparts require their arguments to be Sets.

    In boolean context Set is True if it is not empty and False if it is empty.
    """

    def __init_from_notation(self, notation):

        a = None
        for part in notation.split(','):
            part = part.strip()

            if part.startswith('{') and part.endswith('}'):
                scalar = parse_value(part[1:-1])
                if not is_finite(scalar):
                    raise ValueError('scalar %s must be finite' % scalar)
                if self.pieces:
                    pre = self.pieces[-1]
                    if isinstance(pre, Interval):
                        pre = pre.b.value
                    if pre >= scalar:
                        raise ValueError('%s >= %s!' % (pre, scalar))
                self.pieces.append(scalar)

            else:
                endpoint = Endpoint(part)
                if a is None:
                    a = endpoint
                else:
                    interval = Interval(a, endpoint)
                    if self.pieces:
                        pre = self.pieces[-1]
                        if isinstance(pre, Interval):
                            if pre.b > interval.a:
                                raise ValueError('%s > %s!' % (pre.b, interval.a))
                            if are_bounding(pre.b, interval.a):
                                raise ValueError('%s and %s have no gap!' % (pre.b, interval.a))
                        else:
                            if pre >= interval.a.value:
                                raise ValueError('%s >= %s!' % (pre, interval.a))
                    self.pieces.append(interval)
                    a = None

        if a is not None:
            raise ValueError('Invalid notation')

    @_assert_pieces_are_ascending
    def __init__(self, arg=None):
        # TODO: init from interval?
        if isinstance(arg, Set):
            # Init from Set
            # TODO: "arg" is unclear signature
            self.pieces = _copy_pieces(arg.pieces)
            return
        self.pieces = []
        if arg is None:
            # Init empty Set from None
            return
        elif isinstance(arg, string_types):
            # Init from notation string
            self.__init_from_notation(arg)
        else:
            # Init from iterable of intervals and/or scalars.
            for p in arg:
                self.add(p)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, self.pieces)

    @property
    def notation(self):
        chunks = []
        for i in self.pieces:
            if isinstance(i, Interval):
                chunks.append(i.notation)
            else:
                chunks.append('{%s}' % i)
        return ', '.join(chunks)

    def __bool__(self):
        return len(self.pieces) > 0

    def __nonzero__(self):
        return len(self.pieces) > 0

    def search(self, x, lo=0, hi=None):
        """
        Search scalar x in Set.
        Return tuple of two elements:
            the index where to insert x in list of Set pieces.
            piece that contains x or equals to x, or None if none found.

        Implements Binary search.

        Optional args lo (default 0) and hi (default len(self.pieces)) bound the
            slice of self.pieces to be searched.
        """
        if lo < 0:
            raise ValueError('lo must be non-negative')
        if hi is None:
            hi = len(self.pieces)
        while lo < hi:
            mid = (lo+hi) // 2
            piece = self.pieces[mid]
            if isinstance(piece, Interval):
                start, end = piece.a, piece.b
            else:
                start, end = piece, piece
            if end < x:
                lo = mid + 1
            elif start > x:
                hi = mid
            else:
                return mid, piece

        return lo, None

    def __contains__(self, x):
        """
        x in self
        Test scalar or interval x for membership in Set.
        Note that if x is interval, returning True does not mean that one of
        intervals equals to x, because there can be an interval larger than x.
        """
        if isinstance(x, Interval):
            _, piece = self.search(x.a)
            return piece is not None and is_interval(piece) and x.b <= piece.b
        else:
            return self.search(x)[1] is not None
        
    @_assert_pieces_are_ascending
    def __invert__(self):
        """
        ~self
        Return a new Set that is a compliment of the Set.
        Double inversion (~~self) returns Set that is equal to self.
        """
        new = Set()
        if not self.pieces:
            new.pieces.append(unbounded.copy())
            return new
        if self.pieces[0] == unbounded.copy():
            return new
        # Get plain list of endpoints from original Set.
        endpoints = []
        for i in self.pieces:
            if isinstance(i, Interval):
                endpoints += [i.a, i.b]
            else:
                e1 = Endpoint(i, '[')
                e2 = Endpoint(i, ']')
                endpoints += [e1, e2]
        # Make sure the first endpoint is either -inf or inverted original one.
        if endpoints[0].value == neg_inf:
            del endpoints[0]
            endpoints[0] = ~endpoints[0]
        else:
            endpoints.insert(0, Endpoint('(-inf'))
        # Make sure the last endpoint is either inf or inverted original one.
        if endpoints[-1].value == inf:
            del endpoints[-1]
            endpoints[-1] = ~endpoints[-1]
        else:
            endpoints.append(Endpoint('inf)'))
        # Invert inner endpoints.
        endpoints[1:-1] = [~e for e in endpoints[1:-1]]
        # Construct new Set`s intervals from endpoint pairs.
        # If values of endpoints are same add scalar.
        for a, b in zip(endpoints[::2], endpoints[1::2]):
            if a.value == b.value:
                p = a.value
            else:
                p = Interval(a, b)
            new.pieces.append(p)

        return new

    def __eq__(self, other):
        """
        self == other
        Test whether the Set contains all the pieces of the other and vice versa.
        """
        return isinstance(other, Set) and self.pieces == other.pieces

    def __ne__(self, other):
        """
        self != other
        Test whether the Set contains anything that the other does not contain or vice versa.
        """
        return not isinstance(other, Set) or self.pieces != other.pieces

    def __gt__(self, other):
        """
        self > other
        Test whether the Set is a proper superset of the other.
        """
        if not isinstance(other, Set):
            raise TypeError('Can only compare to an Set')
        return self != other and self >= other

    def __ge__(self, other):
        """
        self >= other
        Test if the other has not anything that is not in the Set.
        """
        if not isinstance(other, Set):
            raise TypeError('Can only compare to an Set')
        lo = 0
        X = iter(other.pieces)
        try:
            x = next(X)
            while True:
                xa, xb = isinstance(x, Interval) and (x.a, x.b) or (x, x)
                lo, p = self.search(xa, lo=lo)
                if p is None:
                    return False
                pa, pb = isinstance(p, Interval) and (p.a, p.b) or (p, p)
                if xb > pb:
                    return False
                while True:
                    x = next(X)
                    xa, xb = isinstance(x, Interval) and (x.a, x.b) or (x, x)
                    if xa >= pb or xb == pb:
                        break
                    if xb < pb:
                        continue
                    return False
        except StopIteration:
            return True
        return False

    def issuperset(self, other):
        """Test if the other has not anything that is not in the Set."""
        if isinstance(other, Set):
            return self >= other
        else:
            return self >= Set(other)

    def __le__(self, other):
        """
        self <= other
        Test whether the USSet has not anything that is not in the other.
        """
        if not isinstance(other, Set):
            raise TypeError('Can only compare to an Set')
        return NotImplemented # so that other.__ge__ will be called

    def issubset(self, other):
        """Test whether the USSet has not anything that is not in the other."""
        if isinstance(other, Set):
            return self <= other
        else:
            return self <= Set(other)

    def __lt__(self, other):
        """
        self < other
        Test whether the Set is a proper subset of the other.
        """
        if not isinstance(other, Set):
            raise TypeError('Can only compare to an Set')
        return NotImplemented # so that other.__gt__ will be called

    def __or__(self, other):
        """
        self | other
        Return a new Set that is a union of the Set and the other.
        """
        if not isinstance(other, Set):
            emsg = "unsupported operand type for |: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        new = self.copy()
        lo = 0
        for x in other.pieces:
            lo = new._add(x, lo)
        return new

    @_assert_pieces_are_ascending
    def __ior__(self, other):
        """
        self |= other
        Update the Set, adding pieces from the other.
        """
        if not isinstance(other, Set):
            emsg = "unsupported operand type for |=: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        lo = 0
        for x in other.pieces:
            lo = self._add(x, lo)
        return self
        
    def union(self, *others):
        """Return a new Set that is a union with the Set and all the others."""
        new = self.copy()
        for other in others:
            if isinstance(other, Set):
                lo = 0
                for x in other.pieces:
                    lo = new._add(x, lo)
            else:
                for x in other:
                    new.add(x)
        return new

    @_assert_pieces_are_ascending
    def update(self, *others):
        """Update the Set, adding pieces from all the others."""
        for other in others:
            lo = 0
            for x in other.pieces:
                lo = self._add(x, lo)

    @staticmethod
    def __and(A, B):
        """Return a new Set that is an intersection of A and B."""
        return A - ~B

    def __and__(self, other):
        """
        self & other
        Return a new Set that is an intersection of the Set`s and the other.
        """
        if not isinstance(other, Set):
            emsg = "unsupported operand type for &: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        return Set.__and(self, other)

    @_assert_pieces_are_ascending
    def __iand__(self, other):
        """
        self &= other
        Update the Set, removing everything that is not in the other.
        """
        if not isinstance(other, Set):
            emsg = "unsupported operand type for &=: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        new = Set.__and(self, other)
        self.pieces = new.pieces
        return self

    def intersection(self, *others):
        """
        Return a new Set that is an intersection of the Set`s and all the others.
        """
        new = self.copy()
        for other in others:
            if isinstance(other, Set):
                new = Set.__and(new, other)
            else:
                new = Set.__and(new, Set(other))
        return new

    @_assert_pieces_are_ascending
    def intersection_update(self, *others):
        """Update the Set, removing everything that is not in any of the others."""
        new = self
        for other in others:
            if isinstance(other, Set):
                new = Set.__and(new, other)
            else:
                new = Set.__and(new, Set(other))
        self.pieces = new.pieces

    def isdisjoint(self, other):
        """
        Return True if none of Set`s pieces intersect with the other`s.
        Sets are disjoint if and only if their intersection is the empty Set.
        """
        i = 0
        for x in other.pieces:
            if isinstance(x, Interval):
                i, p = self.search(x.a, i)
                if p is not None:
                    return False
                i2, p = self.search(x.b, i)
                if i2 > i:
                    return False
                if p is not None:
                    return False
            else:
                i, p = self.search(x, i)
                if p is not None:
                    return False
        return True

    @staticmethod
    def __sub(A, B):
        """Subtract Set B from Set A"""
        lo = 0
        for x in B.pieces:
            lo = A._remove(x, lo)
        return A

    def __sub__(self, other):
        """
        self - other
        Return a new Set with everything that is in the Set but not in the other.
        """
        if not isinstance(other, Set):
            emsg = "unsupported operand type for -: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        new = self.copy()
        return Set.__sub(new, other)

    @_assert_pieces_are_ascending
    def __isub__(self, other):
        """
        self -= other
        Update the Set, removing everything found in the other.
        """
        if not isinstance(other, Set):
            emsg = "unsupported operand type for -=: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        return Set.__sub(self, other)

    def difference(self, *others):
        """
        Return a new Set with everything that is in the Set
        but not in any of the others.
        """
        new = self.copy()
        for other in others:
            if isinstance(other, Set):
                Set.__sub(new, other)
            else:
                for x in other:
                    new.remove(x)
        return new

    @_assert_pieces_are_ascending
    def difference_update(self, *others):
        """Update the Set, removing everything found in the others."""
        for other in others:
            if isinstance(other, Set):
                Set.__sub(self, other)
            else:
                for x in other:
                    self.remove(x)

    @staticmethod
    def __xor(A, B):
        """Return a new Set with pieces in either the Set A or B but not in both."""
        return A - B | B - A

    def __xor__(self, other):
        """
        self ^ other
        Return a new Set with pieces in either the Set or the other but not in both."""
        if not isinstance(other, Set):
            emsg = "unsupported operand type for ^: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        return Set.__xor(self, other)

    @_assert_pieces_are_ascending
    def __ixor__(self, other):
        """
        self ^= other
        Update the Set, keeping only pieces found in either Set, but not in both.
        """
        if not isinstance(other, Set):
            emsg = "unsupported operand type for ^=: %s and %s"
            raise TypeError(emsg % (type(self), type(other)))
        new = Set.__xor(self, other)
        self.pieces = new.pieces
        return self

    def symmetric_difference(self, *others):
        """
        Return a new Set with pieces in either the Set or the other but not in both."""
        new = self.copy()
        for other in others:
            if isinstance(other, Set):
                new = Set.__xor(new, other)
            else:
                new = Set.__xor(new, Set(other))
        return new
    
    @_assert_pieces_are_ascending
    def symmetric_difference_update(self, *others):
        """
        Update the Set, keeping only pieces found in either Set, but not in both.
        """
        new = self
        for other in others:
            if isinstance(other, Set):
                new = Set.__xor(new, other)
            else:
                new = Set.__xor(new, Set(other))
        self.pieces = new.pieces

    def _add_scalar(self, x, lo=0):

        if not is_finite(x):
            raise ValueError('x must be finite')
        idx, piece = self.search(x, lo)
        if piece is not None:
            return idx
        
        pieces = self.pieces
        pre = pieces[idx-1] if idx > 0 else None
        nex = pieces[idx] if len(pieces) >= idx+1 else None
        pre, nex = (isinstance(p, Interval) and p or None for p in [pre, nex])

        if pre is not None:
            if pre.b.value == x:
                if nex is not None and nex.a.value == x:
                    # Adding b to (a, b), (b, c)
                    interval = Interval(pre.a.copy(), nex.b.copy())
                    pieces[idx-1:idx+1] = [interval]
                else:
                    # Adding b to (a, b)
                    b = Endpoint(x, ']')
                    pieces[idx-1] = Interval(pre.a.copy(), b)
                return idx
        if nex is not None and nex.a.value == x:
            # Adding a to (a, b)
            a = Endpoint(x, '[')
            pieces[idx] = Interval(a, nex.b.copy())
            return idx
        pieces.insert(idx, x)
        
        return idx + 1
            
    def _add_interval(self, x, lo=0):

        pieces = self.pieces
        idx1, piece1 = self.search(x.a, lo)
        idx2, piece2 = self.search(x.b, idx1)

        a = x.a.copy()
        if piece1 is not None:
            if isinstance(piece1, Interval):
                a = piece1.a.copy()
        elif idx1 > 0:
            pre = pieces[idx1-1]
            if isinstance(pre, Interval):
                if are_bounding(pre.b, x.a):
                    a = pre.a.copy()
                    idx1 -= 1
            elif pre == x.a.value:
                a = Endpoint(pre, '[')
                idx1 -= 1

        b = x.b.copy()
        if piece2 is not None:
            idx2 += 1
            if isinstance(piece2, Interval):
                b = piece2.b.copy()
        elif len(pieces) >= idx2+1:
            nex = pieces[idx2]
            if isinstance(nex, Interval):
                if are_bounding(x.b, nex.a):
                    b = nex.b.copy()
                    idx2 += 1
            elif nex == x.b.value:
                b = Endpoint(nex, ']')
                idx2 += 1

        pieces[idx1:idx2] = [Interval(a, b)]
        return min([idx2, len(self.pieces)])

    def _add(self, x, lo=0):
        """
        Add scalar or interval x to Set, starting from piece at index lo.
        return index of the first piece that does not intersect with x.
        """
        if isinstance(x, Interval):
            return self._add_interval(x, lo)
        else:
            return self._add_scalar(x, lo)
        
    @_assert_pieces_are_ascending
    def add(self, x):
        """Add scalar or interval x to Set, merge ones that intersect."""
        self._add(x)

    def _remove_scalar(self, x, lo=0):

        idx, piece = self.search(x, lo)
        if piece is None:
            return idx
        
        if isinstance(piece, Interval):
            if piece.a.value == x:
                piece.a.open = True
            elif piece.b.value == x:
                piece.b.open = True
            else:
                # Split interval by x.
                b1 = Endpoint(x, ')')
                i1 = Interval(piece.a, b1)
                a2 = Endpoint(x, '(')
                i2 = Interval(a2, piece.b)
                self.pieces[idx:idx+1] = [i1, i2]
        else:
            self.pieces[idx:idx+1] = []

        return idx

    def _remove_interval(self, x, lo=0):

        pieces = self.pieces
        idx1, piece1 = self.search(x.a, lo)
        idx2, piece2 = self.search(x.b, idx1)

        if piece1 is piece2 and piece1 is not None: # same interval
            new_pieces = []
            if x.a.value == piece1.a.value:
                if x.a.open and not piece1.a.open:
                    new_pieces.append(x.a.value)
            else:
                new_pieces.append(Interval(piece1.a, ~x.a))
            if x.b.value == piece1.b.value:
                if x.b.open and not piece1.b.open:
                    new_pieces.append(x.b.value)
            else:
                new_pieces.append(Interval(~x.b, piece2.b))
            pieces[idx1:idx1+1] = new_pieces
            return idx1

        if piece1 is not None:
            if isinstance(piece1, Interval):
                if x.a.value == piece1.a.value:
                    if x.a.open and not piece1.a.open:
                        pieces[idx1] = x.a.value
                        idx1 += 1
                else:
                    piece1.b = ~x.a
                    idx1 += 1

        if piece2 is not None:
            if isinstance(piece2, Interval):
                if x.b.value == piece2.b.value:
                    if x.b.open and not piece2.b.open:
                        pieces[idx2] = x.b.value
                    else:
                        idx2 += 1
                else:
                    piece2.a = ~x.b
            else:
                idx2 += 1

        pieces[idx1:idx2] = []

        return idx1

    def _remove(self, x, lo=0):
        """
        Remove scalar or interval x from Set, starting from piece at index lo.
        return index of the first piece that does not intersect with x.
        """
        if isinstance(x, Interval):
            return self._remove_interval(x, lo)
        else:
            return self._remove_scalar(x, lo)

    @_assert_pieces_are_ascending
    def remove(self, x):
        """Remove scalar or interval x from the Set."""
        self._remove(x)

    def clear(self):
        """Remove all pieces from the Set."""
        self.pieces = []

    def copy(self):
        """
        Return a copy of the Set.
        Intervals are recreated.
        copy is safe as long as endpoint values are of immutable types.
        """
        new = Set()
        new.pieces = _copy_pieces(self.pieces)
        return new

