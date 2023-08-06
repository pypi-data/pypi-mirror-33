"""
Parses Nastran fields
"""
from __future__ import print_function
from typing import Union, Optional
from six import string_types
from pyNastran.bdf.bdf_interface.bdf_card import BDFCard
from pyNastran.utils import integer_types, integer_float_types, float_types


def parse_components(card, ifield, fieldname):
    # type: (BDFCard, int, str) -> str
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field

    Returns
    -------
    components : str
        a string of the dofs '0' or '123456' (not all are required)
    """
    assert isinstance(card, BDFCard), type(card)
    assert isinstance(ifield, int), type(ifield)
    assert isinstance(fieldname, string_types), type(fieldname)
    svalue = card.field(ifield)
    if isinstance(svalue, integer_types):
        pass
    elif svalue is None or '.' in svalue:
        dtype = _get_dtype(svalue)
        msg = ('%s = %r (field #%s) on card must be an integer (not %s).\n'
               'card=%s' % (fieldname, svalue, ifield, dtype, card))
        raise SyntaxError(msg)

    try:
        value = int(svalue)
    except ValueError:
        dtype = _get_dtype(svalue)
        msg = ('%s = %r (field #%s) on card must be an integer (not %s).\n'
               'card=%s' % (fieldname, svalue, ifield, dtype, card))
        raise SyntaxError(msg)
    if value > 0 and isinstance(svalue, string_types):
        if '0' in svalue:
            value2 = str(svalue).replace('0', '')
            msg = ('%s = %r (field #%s) on card must contain 0 or %s (not both).\n'
                   'card=%s' % (fieldname, svalue, ifield, value2, card))
            raise SyntaxError(msg)
    svalue2 = str(value)
    svalue3 = ''.join(sorted(svalue2))
    for i, component in enumerate(svalue3):
        if component not in '0123456':
            msg = ('%s = %r (field #%s) on card contains an invalid component %r.\n'
                   'card=%s' % (fieldname, svalue, ifield, component, card))
            raise SyntaxError(msg)
        if component in svalue3[i + 1:]:
            msg = ('%s = %r (field #%s) on card must not contain duplicate entries.\n'
                   'card=%s' % (fieldname, svalue, ifield, card))
            raise SyntaxError(msg)
    return svalue3

def components_or_blank(card, ifield, fieldname, default=None):
    # type: (BDFCard, int, str, Optional[str]) -> str
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : str, None
        the default value for the field (default=None)

    Returns
    -------
    components : str
        a string of the dofs '0' or '123456' (not all are required)
    """
    assert isinstance(card, BDFCard), type(card)
    assert isinstance(ifield, int), type(ifield)
    assert isinstance(fieldname, string_types), type(fieldname)
    svalue = card.field(ifield)
    if svalue is None:
        return default
    elif isinstance(svalue, integer_types):
        svalue = str(svalue)
    else:
        svalue = svalue.strip()

    if svalue:
        return parse_components(card, ifield, fieldname)
    else:
        return default

def blank(card, ifield, fieldname, default=None):
    # type: (BDFCard, int, str, None) -> None
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : None
        the default value for the field (default=None)
    """
    assert isinstance(card, BDFCard), type(card)
    assert isinstance(ifield, int), type(ifield)
    assert isinstance(fieldname, string_types), type(fieldname)
    svalue = card.field(ifield)
    if svalue is None:
        return default

    if isinstance(svalue, string_types):
        svalue = svalue.strip().upper()
        if len(svalue) == 0:
            return default
    dtype = _get_dtype(svalue)
    raise SyntaxError('%s = %r (field #%s) on card must be blank (not %s).\n'
                      'card=%s' % (fieldname, svalue, ifield, dtype, card))

def field(card, ifield, fieldname):
    # type: (BDFCard, int, str) -> Optional[Union[int, float, str]]
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field

    Returns
    -------
    value : int, float, str, None
        the field value
    """
    assert isinstance(card, BDFCard), type(card)
    assert isinstance(ifield, int), type(ifield)
    assert isinstance(fieldname, string_types), type(fieldname)
    return integer_double_string_or_blank(card, ifield, fieldname, default=None)

def integer_double_string_or_blank(card, ifield, fieldname, default=None):
    # type: (BDFCard, int, str, Union[int, float, str]) -> Optional[Union[int, float, str]]
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : int, float, str, None (default=None)
        the default value for the field

    Returns
    -------
    value : int, float, str, None
        the field value
    """
    svalue = card.field(ifield)

    if isinstance(svalue, integer_float_types):
        return svalue
    elif svalue is None:
        return default

    svalue = svalue.strip().upper()
    if svalue:
        # integer/float/string
        if '.' in svalue or '-' in svalue[1:] or '+' in svalue[1:]:
            # float
            try:
                value = double(card, ifield, fieldname)
            except SyntaxError:
                value = interpret_value(card[ifield], card)
        elif svalue.isdigit():
            # int
            try:
                value = int(svalue)
            except ValueError:
                dtype = _get_dtype(svalue)
                msg = ('%s = %r (field #%s) on card must be an integer, float, '
                       'or string (not %s).\n'
                       'card=%s' % (fieldname, svalue, ifield, dtype, card))
                raise SyntaxError(msg)
        else:
            value = svalue
        return value
    return default

#def assert_int_bounded_range(card, ifield, fieldname, lower=None, upper=None):

def fields(func, card, fieldname, i, j=None):
    """
    .. todo:: improve fieldname
    """
    assert isinstance(card, BDFCard), type(card)
    assert isinstance(fieldname, string_types), type(fieldname)
    function_values = []
    if j is None:
        j = len(card)
    for ii in range(i, j):
        function_values.append(func(card, ii, fieldname + str(ii)))
    return function_values

def modal_components(card, ifield, fieldname):
    # type: (BDFCard, int, str) -> int
    """
    Gets the modal components (allows a -1 value); used by TIC

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    """
    value = integer(card, ifield, fieldname)
    if not(-1 <= value <= 6):
        raise SyntaxError('%s=%s (field #%s) on card must be an integer '
                          '(-1 <= val <= 6).\n'
                          'card=%s' % (fieldname, value, ifield, card))
    return value

def integer(card, ifield, fieldname):
    # type: (BDFCard, int, str) -> int
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    """
    svalue = card.field(ifield)
    if isinstance(svalue, float_types):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    try:
        return int(svalue)
    except(ValueError, TypeError):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

def integer_or_blank(card, ifield, fieldname, default=None):
    # type: (BDFCard, int, str, Optional[int]) -> Optional[int]
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : int, None
        the default value for the field (default=None)
    """
    svalue = card.field(ifield)

    if isinstance(svalue, integer_types):
        return svalue
    elif svalue is None:
        return default
    elif isinstance(svalue, string_types):
        if len(svalue) == 0:
            return default
        elif '.' in svalue or '-' in svalue[1:] or '+' in svalue[1:]:
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be an integer or blank (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))

        try:
            return int(svalue)
        except(ValueError, TypeError):
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be an integer or blank (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))

    dtype = _get_dtype(svalue)
    raise SyntaxError('%s = %r (field #%s) on card must be an integer (not %s).\n'
                      'card=%s' % (fieldname, svalue, ifield, dtype, card))


def double(card, ifield, fieldname):
    # type: (BDFCard, int, str) -> float
    """
    Converts a field into a double

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field

    Returns
    -------
    value : float
        the value from the desired field
    """
    svalue = card.field(ifield)

    if isinstance(svalue, float_types):
        return svalue
    elif isinstance(svalue, integer_types):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be a float (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))
    elif svalue is None or len(svalue) == 0:  ## None
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be a float (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    if svalue.isdigit():
        # if only int
        dtype = _get_dtype(int(svalue))
        raise SyntaxError('%s = %r (field #%s) on card must be a float (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    #svalue = svalue.strip()
    try:
        # 1.0, 1.0E+3, 1.0E-3
        value = float(svalue)
    except TypeError:
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be a float (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))
    except ValueError:
        # 1D+3, 1D-3, 1-3
        try:
            svalue = svalue.upper()
            if 'D' in svalue:
                # 1.0D+3, 1.0D-3
                svalue2 = svalue.replace('D', 'E')
                return float(svalue2)

            # 1.0+3, 1.0-3
            sign = ''
            if svalue[0] in ('+', '-'):
                sign = svalue[0]
                svalue = svalue[1:]
            if '+' in svalue:
                svalue = sign + svalue.replace('+', 'E+')
            elif '-' in svalue:
                svalue = sign + svalue.replace('-', 'E-')

            value = float(svalue)
        except ValueError:
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be a float (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))
    return value

def double_or_blank(card, ifield, fieldname, default=None):
    # type: (BDFCard, int, str, Optional[Union[float]]) -> Optional[Union[float]]
    """
    Gets a double/blank value

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : double, None
        the default value for the field (default=None)
    """
    svalue = card.field(ifield)

    if isinstance(svalue, float_types):
        return svalue
    elif isinstance(svalue, integer_types):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be a float or blank (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))
    elif isinstance(svalue, string_types):
        svalue = svalue.strip().upper()
        if not svalue:
            return default
        try:
            return double(card, ifield, fieldname)
        except:
            if svalue == '.':
                return 0.
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be a float or blank (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))
    return default

def double_or_string(card, ifield, fieldname):
    # type: (BDFCard, int, str) -> Union[float, str]
    """
    Converts a field into a double or a string

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    """
    svalue = card.field(ifield)

    if isinstance(svalue, float_types):
        return svalue
    elif svalue is None or isinstance(svalue, integer_types):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an float or string (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))
    elif isinstance(svalue, string_types):
        svalue = svalue.strip().upper()

    if '.' in svalue or '-' in svalue[1:] or '+' in svalue[1:]:
        # float
        try:
            return double(card, ifield, fieldname)
        except:
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be an float or string (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))
    elif svalue.isdigit():
        # fail
        pass
    elif svalue:
        # string
        if ' ' in svalue:
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be an float or string without a blank space (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))
        elif svalue[0].isdigit() or '.' in svalue or '+' in svalue or '-' in svalue:
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be an float or string without a blank space (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))
        return str(svalue)
    dtype = _get_dtype(svalue)
    raise SyntaxError('%s = %r (field #%s) on card must be an float or string (not %s).\n'
                      'card=%s' % (fieldname, svalue, ifield, dtype, card))


def double_string_or_blank(card, ifield, fieldname, default=None):
    # type: (BDFCard, int, str, Optional[Union[float, str]]) -> Optional[Union[float, str]]
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : double, None
        the default value for the field (default=None)

    Returns
    -------
    value : float / str / None
        the typed value

    :raises SyntaxError: if there is an invalid type
    """
    svalue = card.field(ifield)

    if isinstance(svalue, float_types):
        return svalue
    elif svalue is None:
        return default
    elif isinstance(svalue, string_types):
        svalue = svalue.strip().upper()
    elif isinstance(svalue, integer_types):
        dtype = _get_dtype(svalue)
        msg = ('%s = %r (field #%s) on card must be an float, string, or blank (not %s).\n'
               'card=%s' % (fieldname, svalue, ifield, dtype, card))
        raise SyntaxError(msg)

    if '.' in svalue or '-' in svalue[1:] or '+' in svalue[1:]:
        try:
            return double(card, ifield, fieldname)
        except:
            dtype = _get_dtype(svalue)
            msg = ('%s = %r (field #%s) on card must be a float, string or blank (not %s).\n'
                   'card=%s' % (fieldname, svalue, ifield, dtype, card))
            raise SyntaxError(msg)
    elif svalue.isdigit():
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be a float, string or blank (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))
    elif svalue == '':
        return default
    return svalue

def integer_or_double(card, ifield, fieldname):
    # type: (BDFCard, int, str) -> Union[int, float]
    """
    Converts a field into an integer or double

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field

    Returns
    -------
    value : int/float
        the value with the proper type

    :raises SyntaxError: if there's an invalid type
    """
    svalue = card.field(ifield)

    if isinstance(svalue, integer_float_types):
        return svalue
    elif svalue is None:
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer or float (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    if '.' in svalue or '-' in svalue[1:] or '+' in svalue[1:]:
        # float/exponent
        try:
            value = double(card, ifield, fieldname)
        except ValueError:
            dtype = _get_dtype(svalue)
            raise SyntaxError('%s = %r (field #%s) on card must be a integer or a float (not %s).\n'
                              'card=%s' % (fieldname, svalue, ifield, dtype, card))
    else:
        # int
        try:
            value = int(svalue)
        except(ValueError, TypeError):
            value = interpret_value(svalue, card)
            if isinstance(value, (int, float)):
                return value
            dtype = _get_dtype(svalue)
            msg = ('%s = %r (field #%s) on card must be an integer or a float (not %s).\n'
                   'card=%s' % (fieldname, svalue, ifield, dtype, card))
            raise SyntaxError(msg)
    return value

def integer_double_or_blank(card, ifield, fieldname, default=None):
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : int / float / None
        the default value for the field (default=None)
    """
    svalue = card.field(ifield)

    if isinstance(svalue, integer_float_types):
        return svalue
    elif svalue is None:
        return default

    if svalue:
        # integer/float
        try:
            return integer_or_double(card, ifield, fieldname)
        except:
            dtype = _get_dtype(svalue)
            msg = ('%s = %r (field #%s) on card must be an integer, float, or blank (not %s).\n'
                   'card=%s' % (fieldname, svalue, ifield, dtype, card))
            raise SyntaxError(msg)
    return default

def integer_or_string(card, ifield, fieldname):
    """
    Converts a field into an integer or string

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : int / str
        the default value for the field (default=None)
    """
    svalue = card.field(ifield)

    if isinstance(svalue, integer_types):
        return svalue
    elif isinstance(svalue, float_types):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer or string (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))
    elif svalue is None:
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer or string (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    try:
        value = int(svalue)
        return value
    except ValueError:
        pass

    if svalue[0].isdigit():
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer or string (not %s; '
                          'strings must start with a character).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    # string
    try:
        value = double(card, ifield, fieldname)
    except SyntaxError:
        return str(svalue.upper())

    if isinstance(value, float_types):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer or string (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))


def integer_string_or_blank(card, ifield, fieldname, default=None):
    """
    Converts a field into an integer, string or sets the default using a blank value

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : int, str, None
        the default value for the field (default=None)
    """
    svalue = card.field(ifield)
    if isinstance(svalue, integer_types):
        return svalue
    elif svalue is None:
        return default
    elif isinstance(svalue, float_types):
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an integer or string (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    svalue = svalue.strip()
    if svalue:
        # integer/string
        try:
            return integer_or_string(card, ifield, fieldname)
        except:
            dtype = _get_dtype(svalue)
            msg = ('%s = %r (field #%s) on card must be an integer, string (without a blank), or blank (not %s).\n'
                   'card=%s' % (fieldname, svalue, ifield, dtype, card))
            raise SyntaxError(msg)
    return default

def _get_dtype(value):
    """
    Get the type of the input value in a form that is clear.

    Parameters
    ----------
    value : int/float/str/None
        the value to get the type of

    Returns
    -------
    dtype : str
        the type of the value
    """
    try:
        value = interpret_value(value)
    except:
        pass
    if value is None:
        dtype = 'blank'
    elif isinstance(value, integer_types):
        dtype = 'an integer'
    elif isinstance(value, float):
        dtype = 'a double value=%r' % value
    elif isinstance(value, string_types):
        dtype = 'a string'
    else:
        dtype = str(type(value))
    return dtype


def integer_double_or_string(card, ifield, fieldname):
    """
    Converts a field into an integer, double or a string

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field

    Returns
    -------
    value : varies
        the value of the field
    """
    svalue = card.field(ifield)
    if isinstance(svalue, integer_float_types):
        return svalue

    svalue = str(svalue.strip())
    if svalue:  # integer/float/string
        if '.' in svalue or '-' in svalue or '+' in svalue:
            # float
            value = double(card, ifield, fieldname)
        elif svalue.isdigit():
            # int
            try:
                value = int(svalue)
            except(ValueError, TypeError):
                msg = ('%s = %r (field #%s) on card must be an integer, float, '
                       'or string (not blank).\n'
                       'card=%s' % (fieldname, svalue, ifield, card))
                raise SyntaxError(msg)
        elif ' ' in svalue:
            raise SyntaxError('%s = %r (field #%s) on card must be an integer, float, or string (not a string with a blank).\n'
                              'card=%s' % (fieldname, svalue, ifield, card))
        elif svalue[0].isdigit():
            raise SyntaxError('%s = %r (field #%s) on card must be an integer, float, or string (not a string with a leading integer).\n'
                              'card=%s' % (fieldname, svalue, ifield, card))
        else:
            value = interpret_value(svalue, card)
        return value
    dtype = _get_dtype(svalue)
    raise SyntaxError('%s = %r (field #%s) on card must be an integer, float, or string (not %s).\n'
                      'card=%s' % (fieldname, svalue, ifield, dtype, card))


def string(card, ifield, fieldname):
    """
    Converts a field into a string

    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field

    Returns
    -------
    value : str
        the value of the field
    """
    svalue = card.field(ifield)
    if isinstance(svalue, string_types):
        svalue = svalue.strip()
        if ' ' in svalue:
            raise SyntaxError('%s = %r (field #%s) on card must be an string without a space.\n'
                              'card=%s' % (fieldname, svalue, ifield, card))

    else:
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an string (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    if svalue[0].isdigit() or '.' in svalue or '+' in svalue or '-' in svalue[0]:
        value = integer_or_double(card, ifield, fieldname)
        dtype = _get_dtype(value)
        msg = ('%s = %r (field #%s) on card must be an string with a character (not %s).\n'
               'card=%s' % (fieldname, value, ifield, dtype, card))
        raise SyntaxError(msg)
    if svalue:  # string
        return str(svalue.upper())
    dtype = _get_dtype(svalue)
    msg = ('%s = %r (field #%s) on card must be an string (not %s).\n'
           'card=%s' % (fieldname, svalue, ifield, dtype, card))
    raise SyntaxError(msg)


def string_or_blank(card, ifield, fieldname, default=None):
    """
    Parameters
    ----------
    card : BDFCard()
        BDF card as a list
    ifield : int
        field number
    fieldname : str
        name of field
    default : str, None
        the default value for the field (default=None)

    Returns
    -------
    value : varies
        the value of the field
    """
    svalue = card.field(ifield)
    if svalue is None:
        return default
    elif isinstance(svalue, string_types):
        svalue = svalue.strip().upper()
        if ' ' in svalue:
            raise SyntaxError('%s = %r (field #%s) on card must be an string without a space.\n'
                              'card=%s' % (fieldname, svalue, ifield, card))
        if svalue[0].isdigit() or '.' in svalue or '+' in svalue or '-' in svalue[0]:
            chars = ''.join(list(set('%s.+-' % svalue[0] if svalue[0].isdigit() else '')))
            raise SyntaxError('%s = %r (field #%s) on card must not have the following characters %s\n'
                              'card=%s' % (fieldname, svalue, ifield, chars, card))
    else:
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an string (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    svalue = svalue.strip()
    if svalue.isdigit() or '.' in svalue or '+' in svalue or '-' in svalue[0]:
        dtype = _get_dtype(svalue)
        raise SyntaxError('%s = %r (field #%s) on card must be an string or blank (not %s).\n'
                          'card=%s' % (fieldname, svalue, ifield, dtype, card))

    if svalue:  # string
        return str(svalue.upper())
    return default

# int                    - done
# int/blank              - done
# int/float              - done
# int/float/blank        - done
# int/float/string       - done
# int/float/string/blank - done
# int/string             - done
# int/string/blank       - done

# float              - done
# float/blank        - done
# float/string       - done
# float/string/blank - done

# string       - done
# string/blank - done


def interpret_value(value_raw, card=''):
    # type: (Optional[str], str) -> Union[int, float, str, None]
    """
    Converts a value from nastran format into python format.

    Parameters
    ----------
    raw_value : str
        a string representation of a value
    card : str
        ???

    Returns
    -------
    value : varies
        the Nastran reprentation of the value
    """
    if value_raw is None:
        return None

    try:
        value_in = value_raw.lstrip().rstrip(' *').upper()
    except AttributeError:
        # it's already an int/float
        msg = 'value_raw=%s type=%s' % (value_raw, type(value_raw))
        assert isinstance(value_raw, integer_float_types), msg
        return value_raw

    if len(value_in) == 0:
        # blank / None
        return None

    if value_in[0].isalpha():
        # string
        return value_in

    if '=' in value_in or '(' in value_in or '*' in value_raw:
        return value_raw.strip()

    # int, float, string, exponent
    value_positive = value_in.strip('+-')
    if value_positive.isdigit():
        # int
        return int(value_in)
    try:
        value = float(value_in)
        # float
        return value
    except ValueError:
        pass

    #if('=' in value_in or '(' in value_in or ')' in value_in):
        #print("=()!")
        #return value_in

    # if there are non-floats/scientific notation -> string
    no_ed = list(set(value_in) - set('ED 1234567890+-'))
    word = ''.join(no_ed)
    if word.isalpha():
        # word
        return value_in

    val0 = value_in[0]
    if val0 in ('+', '-'):
        # truncate the sign for now
        value_left = value_in[1:]
    else:
        # inplied positive value
        val0 = '+'
        value_left = value_in

    if val0 == '-':
        factor = -1.
    elif val0 == '+' or val0.isdigit():
        factor = 1.
    else:
        msg = ('the only 2 cases for a float/scientific are +/- for v0...'
               'value_raw=%r val0=%r card=%s' % (value_raw, val0, card))
        raise SyntaxError(msg)

    # dont include the 1st character, find the exponent
    val_minus = value_in.find('-', 1)
    val_plus = value_in.find('+', 1)
    if val_minus > 0:
        sline = value_left.split('-')
        exp_factor = -1.
    elif val_plus > 0:
        sline = value_left.split('+')
        exp_factor = 1.
    else:
        card_msg = ''
        if card:
            card_msg = 'card = %s\n' % card
        msg = ("I thought this was in scientific notation, but I can't find "
               "the exponent sign...\n"
               "value_raw=%r value_left=%r\n%s"
               "You also might have mixed tabs/spaces/commas or misaligned fields."
               % (value_raw, value_left, card_msg))
        raise SyntaxError(msg)

    if sline[0][-1] == 'D':
        sline[0] = sline[0][:-1]

    try:
        sci0 = factor * float(sline[0])
        sci1 = exp_factor * int(sline[1])
    except ValueError:
        msg = "vm=%s vp=%s value_raw=%r sline=%s" % (val_minus, val_plus, value_raw, sline)
        raise SyntaxError('cannot parse sline[0] into a float and sline[1] '
                          'into an integer\n%s\nYou HAVE mixed '
                          'tabs/spaces/commas!  Fix it!' % msg)

    value = sci0 * 10 ** sci1
    # scientific
    return value


#def string_parser(string_in):
    #"""not used"""
    #type_check = ''
    #n = 0
    #for (i, s) in enumerate(string_in):
        #if s in "+-":
            #state = '+'
        #elif s == " ":
            #state = ' '
        #elif s == ".":
            #state = '.'
        #elif s in "eEdD":
            #state = 'e'
        #elif s.isdigit():
            #state = '1'
        #elif s.isalpha() or s in "()*/=]['\"":
            #return 'string'  # string character
        #else:
            #msg = "s=|%r|" % s
            #raise SyntaxError(msg)

        #if i == 0:
            #type_check += state
            #n += 1
        #elif type_check[n - 1] != state:
            #type_check += state
            #n += 1
        #elif state in 'e .+':  # double e, space, dot, plus
            #return 'string'

    #if type_check == ' ':
        #return None

    #type_check = type_check.strip()
    #if type_check in ['1', '+1']:  # integer
        #return int(string_in)

    #elif type_check in ['1.', '1.1', '.1',  # float
                        #'+1.', '+1.1', '+.1']:
        #return float(string_in)

    #elif type_check in ['1.1e1', '1.1e+1', '1.e1', '1.e+1',  # python scientific
                        #'+1.1e1', '+1.1e+1', '+1.e1', '+1.e+1',
                        #'.1e1', '.1e+1', '+.1e1', '+.1e+1', ]:
        #return float(string_in)

    #elif type_check in ['1+1', '+1+1', '.1+1', '+.1+1']:  # nastran scientific
        #string_reversed = string_in[::-1]
        #i = string_reversed.index('+')
        #list_string = list(string_in)
        #list_string.insert(-i - 1, 'e')

        #out = ''.join(list_string)
        #return float(out)
    #else:
        ## string
        #return string_in

    #print("type_check = %r" % type_check)
    #raise RuntimeError('error parsing a card...this should never happen...')


#if __name__ == '__main__':  # pragma: no cover
    #pass
    #print(string_parser('123'))
    #print(string_parser('+123'))
    #print(string_parser('.234'))
    #print(string_parser('+.234'))
    #print(string_parser('-.234'))
    #print(string_parser('1+5'))
    #print("abc = %r" % string_parser('abc'))
    #print("eeg = %r" % string_parser('eeg'))
    #print("e1 = %r" % string_parser('\T'))
    #print(string_parser('.e1'))
