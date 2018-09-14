"""PySimpleValidate
By Al Sweigart al@inventwithpython.com

The validate* functions in this module accept a `value` argument and raise a
`ValidationException` if it doesn't pass validation.

If `value` was valid, the function returns. The return value is the form of
the value that the validation function has accepted as value. This could
include any transformations such as stripping whitespace from the ends.
If the validation function returns because the value validates against one of
the allowlist regexes, the value is returned.

The following (hopefully self-descriptive) validation functions are implemented
in this module:

* `validateNum()`
* `validateInt()`
* `validateFloat()`
* `validateChoice()`
* `validateDate()`
* `validateTime()`
* `validateDatetime()`
* `validateRegex()`
* `validateRegexStr()`
* `validateURL()`
* `validateYesNo()`
* `validateState
* `validateMonth()`
* `validateDayOfWeek()`
* `validateDayOfMonth()`

These validation functions have the following common parameters:

* `value` (str): The value being validated as a number.
* `blank` (bool): If `False`, a blank string for value will be accepted. Defaults to `False`.
* `strip` (bool, str, None): If `True`, whitespace is stripped from `value`. If a str, the characters in it are stripped from value. If `None`, nothing is stripped. Defaults to `True`.
* `allowlistRegexes` (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers. Defaults to `None`.
* `blocklistRegexes` (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation. Defaults to `None`.

Further, the text-based validators have the following common parameters:

* `caseSensitive` (bool): If `True`, `value` must match the exact casing of an acceptable response. If `False`, any casing can be used. Defaults to `False`.

"""

from __future__ import absolute_import, division, print_function

import calendar
import datetime
import re
import time

__version__ = '0.1.3'

MAX_ERROR_STR_LEN = 50 # Used by _errstr()

# From https://stackoverflow.com/a/5284410/1893164
IPV4_REGEX = re.compile(r"""((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}""")

# From https://stackoverflow.com/a/17871737/1893164
IPV6_REGEX = re.compile(r"""(
([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|          # 1:2:3:4:5:6:7:8
([0-9a-fA-F]{1,4}:){1,7}:|                         # 1::                              1:2:3:4:5:6:7::
([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|         # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|  # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|  # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|  # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|  # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|       # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
:((:[0-9a-fA-F]{1,4}){1,7}|:)|                     # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|     # fe80::7:8%eth0   fe80::7:8%1     (link-local IPv6 addresses with zone index)
::(ffff(:0{1,4}){0,1}:){0,1}
((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}
(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|          # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255  (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
([0-9a-fA-F]{1,4}:){1,4}:
((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}
(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])           # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
)""", re.VERBOSE)

URL_REGEX = re.compile(r"""(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)""")

STATES = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'} # TODO - make STATES a dictionary mapping abbreviation to full name
STATES_UPPER = dict([(abbrev, STATES[abbrev].upper()) for abbrev in STATES.keys()])

MONTHS = {'JAN': 'January', 'FEB': 'February', 'MAR': 'March', 'APR': 'April', 'MAY': 'May', 'JUN': 'June', 'JUL': 'July', 'AUG': 'August', 'SEP': 'September', 'OCT': 'October', 'NOV': 'November', 'DEC': 'December'}

MONTH_NAMES = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

DAYS_OF_WEEK = {'SUN': 'Sunday', 'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday', 'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday'}

DEFAULT_BLOCKLIST_RESPONSE = 'This response is invalid.'


class PySimpleValidateException(Exception):
    '''Base class for exceptions raised when PySimpleValidate functions are
    misused. This doesn't represent a validation failure.'''
    pass


class ValidationException(Exception):
    """Raised when a validation function fails to validate the value."""
    pass


def _(s):
    '''This _() function is a stub for implementing gettext and I18N for PySimpleValidate.'''
    return s


def _errstr(value):
    """Returns the value str, truncated to MAX_ERROR_STR_LEN characters. If it's
    truncated, the returned value will have '...' on the end."""
    value = str(value) # We won't make the caller convert value to a string each time.
    if len(value) > MAX_ERROR_STR_LEN:
        return value[:MAX_ERROR_STR_LEN] + '...'
    else:
        return value


def _getStrippedValue(value, strip=True):
    """Like the strip() str method, except the strip argument describes different behavior:
    If the strip argument is the Boolean True value, whitespace is stripped.
    If the strip argument is a string, the characters in the string are stripped.
    If the strip argument is None, nothing is stripped."""
    if strip is True:
        value = value.strip() # Call strip() with no arguments to strip whitespace.
    elif isinstance(strip, str):
        value = value.strip(strip) # Call strip(), passing the strip argument.
    return value


def _raiseValidationException(standardExcMsg, customExcMsg=None):
    if customExcMsg is None:
        raise ValidationException(str(standardExcMsg))
    else:
        raise ValidationException(str(customExcMsg))


def _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg=None):
    """Returns a tuple of two values: the first is a bool that tells the caller
    if they should immediately return True, the second is a new, possibly stripped
    value for the calling validation function's `value` parameter.

    This function is called by the validate*() functions to perform some common
    housekeeping."""

    # TODO - add a allowlistFirst and blocklistFirst to determine which is checked first. (Right now it's allowlist)

    value = str(value)

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    # Validate for blank values.
    if not blank and value == '':
        # value is blank but blanks aren't allowed.
        _raiseValidationException(_('Blank values are not allowed.'), excMsg)
    elif blank and value == '':
        return True, value

    # Check the allowlistRegexes.
    if allowlistRegexes is not None:
        for regex in allowlistRegexes:
            if re.search(regex, value) is not None:
                return True, value

    # Check the blocklistRegexes.
    if blocklistRegexes is not None:
        for blocklistRegexesed in blocklistRegexes:
            if isinstance(blocklistRegexesed, str):
                regex, response = blocklistRegexesed, DEFAULT_BLOCKLIST_RESPONSE
            else:
                regex, response = blocklistRegexesed

            if re.search(regex, value) is not None:
                _raiseValidationException(response, excMsg) # value is on a blocklist

    return False, value


def _validateGenericParameters(blank, strip, allowlistRegexes, blocklistRegexes):
    """Returns None if the blank, strip, and blocklistRegexes parameters that all
    of PySimpleValidate's validation functions have. Raises a PySimpleValidateException
    if any of the arguments are invalid."""

    if not isinstance(blank, bool):
        raise PySimpleValidateException('blank argument must be a bool')

    if not isinstance(strip, (bool, str, type(None))):
        raise PySimpleValidateException('strip argument must be a bool, None, or str')

    if allowlistRegexes is None:
        allowlistRegexes = [] # allowlistRegexes defaults to a blank list.

    try:
        len(allowlistRegexes) # Make sure allowlistRegexes is a sequence.
    except:
        raise PySimpleValidateException('allowlistRegexes must be a sequence of regex_strs')
    for response in allowlistRegexes:
        if not isinstance(response[0], str):
            raise PySimpleValidateException('allowlistRegexes must be a sequence of regex_strs')


    if blocklistRegexes is None:
        blocklistRegexes = [] # blocklistRegexes defaults to a blank list.

    try:
        len(blocklistRegexes) # Make sure blocklistRegexes is a sequence of (regex_str, str) or strs.
    except:
        raise PySimpleValidateException('blocklistRegexes must be a sequence of (regex_str, str) tuples or regex_strs')
    for response in blocklistRegexes:
        if isinstance(response, str):
            continue
        if len(response) != 2:
            raise PySimpleValidateException('blocklistRegexes must be a sequence of (regex_str, str) tuples or regex_strs')
        if not isinstance(response[0], str) or not isinstance(response[1], str):
            raise PySimpleValidateException('blocklistRegexes must be a sequence of (regex_str, str) tuples or regex_strs')


def _validateParamsFor_validateNum(min=None, max=None, lessThan=None, greaterThan=None):
    """Raises an exception if the arguments are invalid. This is called by
    the validateNum(), validateInt(), and validateFloat() functions to check its arguments. This code was
    refactored out to a separate function so that the PyInputPlus module (or
    other modules) could check their parameters' arguments for validateChoice
    """

    if (min is not None) and (greaterThan is not None):
        raise PySimpleValidateException('only one argument for min or greaterThan can be passed, not both')
    if (max is not None) and (lessThan is not None):
        raise PySimpleValidateException('only one argument for max or lessThan can be passed, not both')

    if (min is not None) and (max is not None) and (min > max):
        raise PySimpleValidateException('the min argument must be less than or equal to the max argument')
    if (min is not None) and (lessThan is not None) and (min >= lessThan):
        raise PySimpleValidateException('the min argument must be less than the lessThan argument')
    if (max is not None) and (greaterThan is not None) and (max <= greaterThan):
        raise PySimpleValidateException('the max argument must be greater than the greaterThan argument')

    for name, val in (('min', min), ('max', max),
                      ('lessThan', lessThan), ('greaterThan', greaterThan)):
        if not isinstance(val, (int, float, type(None))):
            raise PySimpleValidateException(name + ' argument must be int, float, or NoneType')


def validateStr(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=None, blocklistRegexes=blocklistRegexes)
    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)

    return value


def validateNum(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, _numType='num',
                min=None, max=None, lessThan=None, greaterThan=None, excMsg=None):
    """Returns an int or float of value if it passes validation. Raises an
    exception if ValidationException if value fails validation.

    The value can pass validation if it is a number, either int or float.

    Args:
        value (str): The value being validated as a number.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        allowlistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blocklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
        min (int, float): The (inclusive) minimum value for the value to pass validation.
        max (int, float): The (inclusive) maximum value for the value to pass validation.
        lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
        greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.

    If you specify min or max, you cannot also specify lessThan or greaterThan.
    """

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=None, blocklistRegexes=blocklistRegexes)
    _validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    # Validate the value's type (and convert value back to a number type).
    if (_numType == 'num' and '.' in value):
        # We are expecting a "num" (float or int) type and the user entered a float.
        try:
            value = float(value)
        except:
            _raiseValidationException(_('%r is not a number.') % (_errstr(value)), excMsg)
    elif (_numType == 'num' and '.' not in value):
        # We are expecting a "num" (float or int) type and the user entered an int.
        try:
            value = int(value)
        except:
            _raiseValidationException(_('%r is not a number.') % (_errstr(value)), excMsg)
    elif _numType == 'float':
        try:
            value = float(value)
        except:
            _raiseValidationException(_('%r is not a float.') % (_errstr(value)), excMsg)
    elif _numType == 'int':
        try:
            if float(value) % 1 != 0:
                # The number is a float that doesn't end with ".0"
                _raiseValidationException(_('%r is not an integer.') % (_errstr(value)), excMsg)
            value = int(float(value))
        except:
            _raiseValidationException(_('%r is not an integer.') % (_errstr(value)), excMsg)

    # Validate against min argument.
    if min is not None and value < min:
        _raiseValidationException(_('Input must be at minimum %s.') % (min), excMsg)

    # Validate against max argument.
    if max is not None and value > max:
        _raiseValidationException(_('Input must be at maximum %s.') % (max), excMsg)

    # Validate against max argument.
    if lessThan is not None and value >= lessThan:
        _raiseValidationException(_('Input must be less than %s.') % (lessThan), excMsg)

    # Validate against max argument.
    if greaterThan is not None and value <= greaterThan:
        _raiseValidationException(_('Input must be greater than %s.') % (greaterThan), excMsg)

    return value


def validateInt(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None,
                min=None, max=None, lessThan=None, greaterThan=None, excMsg=None):
    """Returns an int of value if it passes validation. Raises an
    exception if ValidationException if value fails validation.

    The value can pass validation if it is an int.

    Args:
        value (str): The value being validated as a number.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        allowlistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blocklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
        min (int, float): The (inclusive) minimum value for the value to pass validation.
        max (int, float): The (inclusive) maximum value for the value to pass validation.
        lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
        greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.

    If you specify min or max, you cannot also specify lessThan or greaterThan.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateInt('42')
    42
    >>> pysv.validateInt('forty two')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'forty two' is not an integer.
    """
    return validateNum(value=value, blank=blank, strip=strip, allowlistRegexes=None,
                       blocklistRegexes=blocklistRegexes, _numType='int', min=min, max=max,
                       lessThan=lessThan, greaterThan=greaterThan)


def validateFloat(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None,
                min=None, max=None, lessThan=None, greaterThan=None, excMsg=None):
    """Returns a float of value if it passes validation. Raises an
    exception if ValidationException if value fails validation.

    The value can pass validation if it is a float.

    Args:
        value (str): The value being validated as a number.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        allowlistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blocklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
        min (int, float): The (inclusive) minimum value for the value to pass validation.
        max (int, float): The (inclusive) maximum value for the value to pass validation.
        lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
        greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.

    If you specify min or max, you cannot also specify lessThan or greaterThan.

    >>> import pysimplevalidate as pysv

    >>> pysv.validateFloat('3.14')
    3.14

    >>> pysv.validateFloat('pi')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'pi' is not a float.

    >>> pysv.validateFloat('3')
    3.0

    >>> pysv.validateFloat('3', min=3)
    3.0

    >>> pysv.validateFloat('3', greaterThan=3)
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: Input must be greater than 3.
    """

    # TODO: Accept "e" formatted numbers, like 1.0000000000000001e-48.

    return validateNum(value=value, blank=blank, strip=strip, allowlistRegexes=None,
                       blocklistRegexes=blocklistRegexes, _numType='float', min=min, max=max,
                       lessThan=lessThan, greaterThan=greaterThan)


def _validateParamsFor_validateChoice(choices, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None,
                   numbered=False, lettered=False, caseSensitive=False, excMsg=None):
    """Raises an exception if the arguments are invalid. This is called by
    the validateChoice() function to check its arguments. This code was
    refactored out to a separate function so that the PyInputPlus module (or
    other modules) could check their parameters' arguments for validateChoice
    """

    if not isinstance(caseSensitive, bool):
        raise PySimpleValidateException('caseSensitive argument must be a bool')

    try:
        len(choices)
    except:
        raise PySimpleValidateException('choices arg must be a sequence')
    if blank == False and len(choices) < 2:
        raise PySimpleValidateException('choices must have at least two items if blank is False')
    elif blank == True and len(choices) < 1:
        raise PySimpleValidateException('choices must have at least one item')


    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=None, blocklistRegexes=blocklistRegexes)

    for choice in choices:
        if not isinstance(choice, str):
            raise PySimpleValidateException('choice %r must be a string' % (_errstr(choice)))
    if lettered and len(choices) > 26:
        raise PySimpleValidateException('lettered argument cannot be True if there are more than 26 choices')
    if numbered and lettered:
        raise PySimpleValidateException('numbered and lettered arguments cannot both be True')

    if len(choices) != len(set(choices)):
        raise PySimpleValidateException('duplicate entries in choices argument')

    if not caseSensitive and len(choices) != len(set([choice.upper() for choice in choices])):
        raise PySimpleValidateException('duplicate case-insensitive entries in choices argument')


def validateChoice(value, choices, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None,
                   numbered=False, lettered=False, caseSensitive=False, excMsg=None):
    """Returns the selected choice if it's one of the values in `choices`. Raises
    an exception if ValidationException if value fails validation.

    If `lettered` is `True`, lower or uppercase letters will be accepted regardless
    of what `caseSensitive` is set to. The `caseSensitive` argumnet only matters
    for matching with the text of the strings in `choices`.

    Args:
        value (str): The value being validated.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        allowlistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blocklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        numbered (bool): TODO
        lettered (bool): TODO
        caseSensitive (bool): TODO

    Returns the choice selected as it appeared in `choices`. That is, if `'cat'`
    was a choice and the user entered `'CAT'` while caseSensitive is `False`,
    this function will return `'cat'`.


    >>> import pysimplevalidate as pysv
    >>> pysv.validateChoice('dog', ['dog', 'cat', 'moose'])
    'dog'

    >>> pysv.validateChoice('DOG', ['dog', 'cat', 'moose'])
    'dog'

    >>> pysv.validateChoice('2', ['dog', 'cat', 'moose'], numbered=True)
    'cat'

    >>> pysv.validateChoice('a', ['dog', 'cat', 'moose'], lettered=True)
    'dog'

    >>> pysv.validateChoice('C', ['dog', 'cat', 'moose'], lettered=True)
    'moose'

    >>> pysv.validateChoice('dog', ['dog', 'cat', 'moose'], lettered=True)
    'dog'

    >>> pysv.validateChoice('spider', ['dog', 'cat', 'moose'])
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'spider' is not a valid choice.
    """

    # Validate parameters.
    _validateParamsFor_validateChoice(choices=choices, blank=blank, strip=strip, allowlistRegexes=None,
        blocklistRegexes=blocklistRegexes, numbered=numbered, lettered=lettered, caseSensitive=caseSensitive)

    if '' in choices:
        # `blank` needs to be set to True here, otherwise '' won't be accepted as a choice.
        blank = True

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    # Validate against choices.
    if value in choices:
        return value
    if numbered and value.isdigit() and 0 < int(value) <= len(choices): # value must be 1 to len(choices)
        # Numbered options begins at 1, not 0.
        return choices[int(value) - 1] # -1 because the numbers are 1 to len(choices) but the index are 0 to len(choices) - 1
    if lettered and len(value) == 1 and value.isalpha() and 0 < ord(value.upper()) - 64 <= len(choices):
        # Lettered options are always case-insensitive.
        return choices[ord(value.upper()) - 65]
    if not caseSensitive and value.upper() in [choice.upper() for choice in choices]:
        # Return the original item in choices that value has a case-insensitive match with.
        return choices[[choice.upper() for choice in choices].index(value.upper())]

    _raiseValidationException(_('%r is not a valid choice.') % (_errstr(value)), excMsg)


def _validateParamsFor__validateToDateTimeFormat(formats, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)
    if formats is None:
        raise PySimpleValidateException('formats parameter must be specified')

    if isinstance(formats, str):
        raise PySimpleValidateException('formats argument must be a non-str sequence of strftime format strings')

    try:
        len(formats)
    except:
        raise PySimpleValidateException('formats argument must be a non-str sequence of strftime format strings')

    for format in formats:
        try:
            time.strftime(format) # This will raise an exception if the format is invalid.
        except:
            raise PySimpleValidateException('formats argument contains invalid strftime format strings')


def _validateToDateTimeFormat(value, formats, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    # Validate parameters.
    _validateParamsFor__validateToDateTimeFormat(formats, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    # Validate against the given formats.
    for format in formats:
        try:
            return datetime.datetime.strptime(value, format)
        except ValueError:
            continue # If this format fails to parse, move on to the next format.

    _raiseValidationException(_('%r is not a valid time.') % (value), excMsg)


def validateTime(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None,
                 formats=('%H:%M:%S', '%H:%M', '%X'), excMsg=None):
    """Returns True if value is a time that passes validation. Raises an
    exception if ValidationException if value fails validation.

    Args:
        value (str): The value being validated as a time.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        allowlistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blocklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid time.
    """

    # TODO - handle this

    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        dt = _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)
        return datetime.time(dt.hour, dt.minute, dt.second, dt.microsecond)
    except ValidationException:
        _raiseValidationException(_('%r is not a valid time that follows the formats argument.') % (_errstr(value)), excMsg)


def validateDate(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None,
                 formats=('%Y/%m/%d', '%y/%m/%d', '%m/%d/%Y', '%m/%d/%y', '%x'), excMsg=None):
    """Returns True if value is a date that passes validation. Raises an
    exception if ValidationException if value fails validation.

    Args:
        value (str): The value being validated as a time.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        allowlistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blocklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid date.
    """
    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        dt = _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)
        return datetime.date(dt.year, dt.month, dt.day)
    except ValidationException:
        _raiseValidationException(_('%r is not a valid date that follows the formats argument.') % (_errstr(value)), excMsg)


def validateDatetime(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None,
                     formats=('%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%x %H:%M:%S',
                              '%Y/%m/%d %H:%M', '%y/%m/%d %H:%M', '%m/%d/%Y %H:%M', '%m/%d/%y %H:%M', '%x %H:%M',
                              '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%x %H:%M:%S'), excMsg=None):
    """Returns True if value is a datetime that passes validation. Raises an
    exception if ValidationException if value fails validation.

    Args:
        value (str): The value being validated as a time.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        allowlistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blocklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid datetime.
    """

    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        return _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)
    except ValidationException:
        _raiseValidationException(_('%r is not a valid date and time that follows the formats argument.') % (_errstr(value)), excMsg)





# TODO: The rest of these functions are under development.

def validateFilename(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, mustExist=False, excMsg=None):
    # TODO - finish this.
    if value.endswith(' '):
        _raiseValidationException(_('%r is not a valid filename because it ends with a space.') % (_errstr(value)), excMsg)
    raise NotImplementedError()


def validateFilepath(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, mustExist=False):
    # TODO - finish this.
    raise NotImplementedError()


def validateIp(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    # Reuse the logic in validateRegex()
    try:
        if validateRegex(value=value, regex=IPV4_REGEX, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes):
            return value
        if validateRegex(value=value, regex=IPV6_REGEX, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes):
            return value
    except ValidationException:
        _raiseValidationException(_('%r is not a valid IP address.') % (_errstr(value)), excMsg)


def validateRegex(value, regex, flags=0, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    mo = re.compile(regex, flags).search(value)
    if mo is not None:
        return mo.group()
    else:
        _raiseValidationException(_('%r does not match the specified pattern.') % (_errstr(value)), excMsg)


def validateRegexStr(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    # TODO - I'd be nice to check regexes in other languages, i.e. JS and Perl.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    try:
        return re.compile(value)
    except Exception as ex:
        _raiseValidationException(_('%r is not a valid regular expression: %s') % (_errstr(value), ex), excMsg)


def validateURL(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    # Reuse the logic in validateRege()
    try:
        result = validateRegex(value=value, regex=URL_REGEX, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)
        if result is not None:
            return result
    except ValidationException:
        _raiseValidationException(_('%r is not a valid URL.') % (value), excMsg)


def validateYesNo(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, yesVal='yes', noVal='no', caseSensitive=False, excMsg=None):
    # Note: Rather than always return True, this function returns the original `yes` or `no` argument, depending on what `value` represents.

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    yesVal = str(yesVal)
    noVal = str(noVal)
    if len(yesVal) == 0:
        raise PySimpleValidateException('yesVal argument must be a non-empty string.')
    if len(noVal) == 0:
        raise PySimpleValidateException('noVal argument must be a non-empty string.')
    if yesVal == noVal:
        raise PySimpleValidateException('yesVal and noVal arguments must be different.')

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    if caseSensitive:
        if value in (yesVal, yesVal[0]):
            return yesVal
        elif value in (noVal, noVal[0]):
            return noVal
    else:
        if value.upper() in (yesVal.upper(), yesVal[0].upper()):
            return yesVal
        elif value.upper() in (noVal.upper(), noVal[0].upper()):
            return noVal

    _raiseValidationException(_('%r is not a valid %s/%s response.') % (_errstr(value), yesVal, noVal), excMsg)


def validateBool(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, trueVal='True', falseVal='False', caseSensitive=False, excMsg=None):
    # Replace the exception messages used in validateYesNo():
    trueVal = str(trueVal)
    falseVal = str(falseVal)
    if len(trueVal) == 0:
        raise PySimpleValidateException('trueVal argument must be a non-empty string.')
    if len(falseVal) == 0:
        raise PySimpleValidateException('falseVal argument must be a non-empty string.')
    if trueVal == falseVal:
        raise PySimpleValidateException('trueVal and falseVal arguments must be different.')

    result = validateYesNo(value, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes, yesVal=trueVal, noVal=falseVal, caseSensitive=caseSensitive, excMsg=None)

    # Return a bool value instead of a string.
    if result == trueVal:
        return True
    elif result == falseVal:
        return False
    else:
        return result # Return `result` if a blank or allowlisted value was entered, or postValidateApplyFunc() transformed the value.


def validateState(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    # TODO - note that this is USA-centric

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value

    if value.upper() in STATES_UPPER.keys(): # check if `value` is a state abbreviation
        return STATES[value.upper()] # It turns out that titlecase is good for all the states.
    elif value.title() in STATES.values(): # check if `value` is a state name
        return value.title()

    _raiseValidationException(_('%r is not a state.') % (_errstr(value)), excMsg)


def validateName():
    raise NotImplementedError()


def validateAddress():
    raise NotImplementedError()


def validatePhone():
    raise NotImplementedError()


def validateMonth(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, monthNames=MONTHS, excMsg=None):

    # returns full month name, e.g. 'January'

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowlistRegexes, blocklistRegexes, excMsg)
    if returnNow:
        return value


    try:
        if (monthNames == MONTHS) and (1 <= int(value) <= 12): # This check here only applies to months, not when validateDayOfWeek() calls this function.
            return MONTH_NAMES[int(value) - 1]
    except:
        pass # continue if the user didn't enter a number 1 to 12.

    # Both month names and month abbreviations will be at least 3 characters.
    if len(value) < 3:
        _raiseValidationException(_('%r is not a month.') % (_errstr(value)), excMsg)

    if value[:3].upper() in monthNames.keys(): # check if `value` is a month abbreviation
        return monthNames[value[:3].upper()] # It turns out that titlecase is good for all the month.
    elif value.upper() in monthNames.values(): # check if `value` is a month name
        return value.title()

    _raiseValidationException(_('%r is not a month.') % (_errstr(value)), excMsg)


def validateDayOfWeek(value, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, dayNames=DAYS_OF_WEEK, excMsg=None):
    # TODO - reuse validateChoice for this function

    # returns full day of the week str, e.g. 'Sunday'

    # Reuses validateMonth.
    try:
        return validateMonth(value, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes, monthNames=DAYS_OF_WEEK)
    except:
        # Replace the exception message.
        _raiseValidationException(_('%r is not a day of the week') % (_errstr(value)), excMsg)


def validateDayOfMonth(value, year, month, blank=False, strip=True, allowlistRegexes=None, blocklistRegexes=None, excMsg=None):
    try:
        daysInMonth = calendar.monthrange(year, month)[1]
    except:
        raise PySimpleValidateException('invalid arguments for year and/or month')

    try:
        return validateInt(value, blank=blank, strip=strip, allowlistRegexes=allowlistRegexes, blocklistRegexes=blocklistRegexes, min=1, max=daysInMonth)
    except:
        # Replace the exception message.
        _raiseValidationException(_('%r is not a day in the month of %s %s') % (_errstr(value), MONTH_NAMES[month], year), excMsg)





if __name__ == '__main__':
    import doctest
    doctest.testmod()