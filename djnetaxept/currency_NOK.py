# -*- coding: utf-8 -*-


def integer_currency_NOK(kr, thousand_sep=' '):
    """Return a string version of the integer value ``kr``, with
       space as the thousand-separator.
    """
    if kr == 0:
        return '0'
    res = ''
    if kr < 0:
        sign = '-'
        kr = -kr
    else:
        sign = ''

    while kr:
        kr, tusen = divmod(kr, 1000)
        res = thousand_sep.join(['%03d' % tusen, res])

    return sign + res.rstrip(' ').lstrip('0')


def fractional_currency_NOK(n):
    """Return a string version of the integer 'cent'-value. Either a two-digit
       string or a dash (as in the last character of: 5,-).
    """
    if n == 0:
        return '-'
    return '%02d' % n


def currency_NOK(n, sep=','):
    """Convert the 'cent'-value ``n`` to a proper NOK string value.
    """
    kr, ore = divmod(n, 100)
    return integer_currecny_NOK(kr) + sep + fractional_currency_NOK(ore)
