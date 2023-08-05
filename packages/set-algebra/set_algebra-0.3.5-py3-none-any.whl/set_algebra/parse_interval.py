

def parse_interval(notation):
    if not isinstance(notation, string_types):
        raise TypeError('notation must be a string, not %s' % type(notation).__name__)

    notation = notation.strip()
    a_str, b_str = notation.split(',')
    if ',' in b_str:
        raise ValueError('There should be one and only one comma in interval notation')

    return parse_endpoint_notation(a_str), parse_endpoint_notation(b_str)

