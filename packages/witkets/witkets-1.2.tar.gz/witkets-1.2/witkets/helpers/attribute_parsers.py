def parse_bool(val):
    if val == 'True' or val == '1':
        return True
    elif val == 'False' or val == '0':
        return False
    raise ValueError()


def _parse_padding(val, numtokens):
    """Parse a padding attribute.

    Paddings can be in one of the forms below:
      - '15' --- pixels (can be passed as string or integer)
      - '<num><unit>' --- number followed by a unit ('c', 'i', 'm' or 'p')
      - '<padding> <padding>' --- space-separated values
      - '(<padding>, <padding>)' --- tuple
      -
    """
    val = val.strip()
    if val.startswith('('):
        no_parenthesis = val.replace('(', '').replace(')', '')
        tokens = no_parenthesis.split(',')
        if len(tokens) != numtokens:
            raise ValueError()
        return tuple(tokens)
    return val


def parse_axispadding(val):
    """Parse axis paddings (one or two dimensions)."""
    return _parse_padding(val, 2)


def parse_allpadding(val):
    """Parse global paddings (one or for dimensions)"""
    return _parse_padding(val, 4)
