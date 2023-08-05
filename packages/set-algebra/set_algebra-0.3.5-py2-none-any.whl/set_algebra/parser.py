from set_algebra.infinity import inf, neg_inf


try:
    string_types = basestring
except NameError:
    string_types = str


def parse_value(value_str):
    """
    Parse numeric string, return either:
    int
    float
    Infinity, NegativeInfinity
    """
    if not isinstance(value_str, string_types):
        raise TypeError('value_str must be a string, not %s' % type(value_str).__name__)

    value_str = value_str.strip()
    if value_str.isdigit() or (value_str[0] == '-' and value_str[1:].isdigit()):
        value = int(value_str)
    elif value_str in ('-inf', 'neg_inf'):
        value = neg_inf
    elif value_str == 'inf':
        value = inf
    else:
        value = float(value_str)

    return value


BOUNDS_TO_OPEN_LEFT_MAPPING = {
    '[': (False, True),
    '(': (True, True),
    ']': (False, False),
    ')': (True, False),
}

OPEN_LEFT_TO_BOUNDS_MAPPING = {v: k for k, v in BOUNDS_TO_OPEN_LEFT_MAPPING.items()}


def parse_bound(bound):
    """
    Given 1 length string, return a tuple of two booleans: (open, left)
    """
    if not isinstance(bound, string_types):
        raise TypeError('bound must be a string, not %s' % type(bound).__name__)

    try:
        return BOUNDS_TO_OPEN_LEFT_MAPPING[bound]
    except KeyError:
        raise ValueError('bound must be one of [](), not %s' % bound)


def parse_endpoint_notation(notation):
    """
    Parse string representing Endpoint (endpoint notation).

    Returns tuple of 3 elements:
        0: int or float instance, or inf or neg_inf
        1: bool indicating whether endpoint is open
        2: bool indicating whether endpoint is left
    Raises ValueError for invalid notation.

    >>> parse_endpoint_notation('[5.7')
    (5.7, False, True)
    >>> parse_endpoint_notation('9]')
    (9, False, False)
    >>> parse_endpoint_notation('inf)')
    (inf, True, False)
    """
    if not isinstance(notation, string_types):
        raise TypeError('notation must be a string, not %s' % type(notation).__name__)

    notation = notation.strip()

    if len(notation) < 2:
        raise ValueError('Invalid Notation')
    if notation[0] in '[(':
        bound, value_str = notation[0], notation[1:]
    elif notation[-1] in '])':
        value_str, bound = notation[:-1], notation[-1]
    else:
        raise ValueError('Invalid notation')

    open, left = BOUNDS_TO_OPEN_LEFT_MAPPING[bound]

    value = parse_value(value_str)

    return value, open, left
