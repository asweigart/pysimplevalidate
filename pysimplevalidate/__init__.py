"""PySimpleValidate
By Al Sweigart al@inventwithpython.com

The validate* functions in this module accept a `value` argument and raise a
`ValidationException` if it doesn't pass validation.

If `value` was valid, the function returns. The meaning of the return value
depends on the particular validation function, but most often is simply `True`.

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
* `validateLiteralRegex()`
* `validateURL()`
* `validateYesNo()`
* `validateState
* `validateStateAbbrev()`
* `validateZipCode()`
* `validateMonth()`
* `validateDayOfWeek()`
* `validateDayOfMonth()`
* `validateYear()`

These validation functions have the following common parameters:

* `value` (str): The value being validated as a number.
* `blank` (bool): If `False`, a blank string for value will be accepted. Defaults to `False`.
* `strip` (bool, str, None): If `True`, whitespace is stripped from `value`. If a str, the characters in it are stripped from value. If `None`, nothing is stripped. Defaults to `True`.
* `whitelistRegexes` (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers. Defaults to `None`.
* `blacklistRegexes` (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation. Defaults to `None`.

Further, the text-based validators have the following common parameters:

* `caseSensitive` (bool): If `True`, `value` must match the exact casing of an acceptable response. If `False`, any casing can be used. Defaults to `False`.

"""

from __future__ import absolute_import, division, print_function

import re
import time

__version__ = '0.1.0'

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

STATES = ('Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming', 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY')
STATES_UPPER = tuple([state.upper() for state in STATES])
MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

DEFAULT_BLACKLIST_RESPONSE = 'This response is invalid.'


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


def _checkWhitelistBlacklist(value, whitelistRegexes, blacklistRegexes):
    """Where whitelistRegexes is a list of regex strings, this function returns True
    if value matches any of the regexes. Otherwise, returns False if the value
    is not on the whitelistRegexes or blacklistRegexes.

    Where blacklistRegexes is a list of ('regex', 'response') tuples or a list of
    regex strings, this function raises a ValidationException with the response
    string as the exception message for the for the first regex that matches."""

    # NOTE: whitelistRegexes and blacklistRegexes aren't validated in this function.

    # Check the whitelistRegexes.
    if whitelistRegexes is not None:
        for regex in whitelistRegexes:
            if re.search(regex, value) is not None:
                return True

    # Check the blacklistRegexes.
    if blacklistRegexes is not None:
        for blacklistRegexesed in blacklistRegexes:
            if isinstance(blacklistRegexesed, str):
                regex, response = blacklistRegexesed, DEFAULT_BLACKLIST_RESPONSE
            else:
                regex, response = blacklistRegexesed

            if re.search(regex, value) is not None:
                # Return the response that matches this regex.
                raise ValidationException(response)

    return False


def _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes):
    """Returns a tuple of two values: the first is a bool that tells the caller
    if they should immediately return True, the second is a new, possibly stripped
    value for the calling validation function's `value` parameter.

    This function is called by the validate*() functions to perform some common
    housekeeping."""

    value = str(value)

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    # Validate for blank values.
    if not blank and value == '':
        # value is blank but blanks aren't allowed.
        raise ValidationException(_('Blank values are not allowed.'))
    elif blank and value == '':
        return True, value

    # Check white and blacklistRegexes.
    if _checkWhitelistBlacklist(value, whitelistRegexes, blacklistRegexes):
        return True, value

    return False, value


def _validateGenericParameters(blank, strip, whitelistRegexes, blacklistRegexes):
    """Returns None if the blank, strip, and blacklistRegexes parameters that all
    of PySimpleValidate's validation functions have. Raises a PySimpleValidateException
    if any of the arguments are invalid."""

    if not isinstance(blank, bool):
        raise PySimpleValidateException('blank argument must be a bool')

    if not isinstance(strip, (bool, str, type(None))):
        raise PySimpleValidateException('strip argument must be a bool, None, or str')

    if whitelistRegexes is None:
        whitelistRegexes = [] # whitelistRegexes defaults to a blank list.

    try:
        len(whitelistRegexes) # Make sure whitelistRegexes is a sequence.
    except:
        raise PySimpleValidateException('whitelistRegexes must be a sequence of regex_strs')
    for response in whitelistRegexes:
        if not isinstance(response[0], str):
            raise PySimpleValidateException('whitelistRegexes must be a sequence of regex_strs')


    if blacklistRegexes is None:
        blacklistRegexes = [] # blacklistRegexes defaults to a blank list.

    try:
        len(blacklistRegexes) # Make sure blacklistRegexes is a sequence of (regex_str, str) or strs.
    except:
        raise PySimpleValidateException('blacklistRegexes must be a sequence of (regex_str, str) tuples or regex_strs')
    for response in blacklistRegexes:
        if isinstance(response, str):
            continue
        if len(response) != 2:
            raise PySimpleValidateException('blacklistRegexes must be a sequence of (regex_str, str) tuples or regex_strs')
        if not isinstance(response[0], str) or not isinstance(response[1], str):
            raise PySimpleValidateException('blacklistRegexes must be a sequence of (regex_str, str) tuples or regex_strs')


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


def validateNum(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None, _numType='num',
                min=None, max=None, lessThan=None, greaterThan=None):
    """Returns True if value is a number that passes validation. Raises an
    exception if ValidationException if value fails validation.

    The value can pass validation if it is a number, either int or float.

    Args:
        value (str): The value being validated as a number.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        whitelistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blacklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
        min (int, float): The (inclusive) minimum value for the value to pass validation.
        max (int, float): The (inclusive) maximum value for the value to pass validation.
        lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
        greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.

    If you specify min or max, you cannot also specify lessThan or greaterThan.
    """

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=None, blacklistRegexes=blacklistRegexes)
    _validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
    if returnNow:
        return True

    # Validate the value's type (and convert value back to a number type).
    if (_numType == 'num' and '.' in value):
        # We are expecting a "num" (float or int) type and the user entered a float.
        try:
            value = float(value)
        except:
            raise ValidationException(_('%r is not a number.') % (_errstr(value)))
    elif (_numType == 'num' and '.' not in value):
        # We are expecting a "num" (float or int) type and the user entered an int.
        try:
            value = int(value)
        except:
            raise ValidationException(_('%r is not a number.') % (_errstr(value)))
    elif _numType == 'float':
        try:
            value = float(value)
        except:
            raise ValidationException(_('%r is not a float.') % (_errstr(value)))
    elif _numType == 'int':
        try:
            if float(value) % 1 != 0:
                # The number is a float that doesn't end with ".0"
                raise ValidationException(_('%r is not an integer.') % (_errstr(value)))
            value = int(float(value))
        except:
            raise ValidationException(_('%r is not an integer.') % (_errstr(value)))

    # Validate against min argument.
    if min is not None and value < min:
        raise ValidationException(_('Input must be at minimum %s.') % (min))

    # Validate against max argument.
    if max is not None and value > max:
        raise ValidationException(_('Input must be at maximum %s.') % (max))

    # Validate against max argument.
    if lessThan is not None and value >= lessThan:
        raise ValidationException(_('Input must be less than %s.') % (lessThan))

    # Validate against max argument.
    if greaterThan is not None and value <= greaterThan:
        raise ValidationException(_('Input must be greater than %s.') % (greaterThan))

    return True


def validateInt(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None,
                min=None, max=None, lessThan=None, greaterThan=None):
    """Returns True if value is a number that passes validation. Raises an
    exception if ValidationException if value fails validation.

    The value can pass validation if it is an int.

    Args:
        value (str): The value being validated as a number.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        whitelistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blacklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
        min (int, float): The (inclusive) minimum value for the value to pass validation.
        max (int, float): The (inclusive) maximum value for the value to pass validation.
        lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
        greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.

    If you specify min or max, you cannot also specify lessThan or greaterThan.
    """
    return validateNum(value=value, blank=blank, strip=strip, whitelistRegexes=None,
                       blacklistRegexes=blacklistRegexes, _numType='int', min=min, max=max,
                       lessThan=lessThan, greaterThan=greaterThan)


def validateFloat(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None,
                min=None, max=None, lessThan=None, greaterThan=None):
    """Returns True if value is a number that passes validation. Raises an
    exception if ValidationException if value fails validation.

    The value can pass validation if it is a float.

    Args:
        value (str): The value being validated as a number.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        whitelistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blacklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
        min (int, float): The (inclusive) minimum value for the value to pass validation.
        max (int, float): The (inclusive) maximum value for the value to pass validation.
        lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
        greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.

    If you specify min or max, you cannot also specify lessThan or greaterThan.
    """

    # TODO: Accept "e" formatted numbers, like 1.0000000000000001e-48.

    return validateNum(value=value, blank=blank, strip=strip, whitelistRegexes=None,
                       blacklistRegexes=blacklistRegexes, _numType='float', min=min, max=max,
                       lessThan=lessThan, greaterThan=greaterThan)


def _validateParamsFor_validateChoice(choices, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None,
                   numbered=False, lettered=False, caseSensitive=False):
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


    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=None, blacklistRegexes=blacklistRegexes)

    for choice in choices:
        if not isinstance(choice, str):
            raise PySimpleValidateException('choice %r must be a string' % (_errstr(choice)))
    if lettered and len(choices) > 26:
        raise PySimpleValidateException('lettered argument cannot be True if there are more than 26 choices')
    if numbered and lettered:
        raise PySimpleValidateException('numbered and lettered arguments cannot both be True')


def validateChoice(value, choices, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None,
                   numbered=False, lettered=False, caseSensitive=False):
    """Returns the selected choice if it's one of the values in `choices`. Raises
    an exception if ValidationException if value fails validation.

    If `lettered` is `True`, lower or uppercase letters will be accepted regardless
    of what `caseSensitive` is set to. The `caseSensitive` argumnet only matters
    for matching with the text of the strings in `choices`.

    Args:
        value (str): The value being validated.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        whitelistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blacklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        numbered (bool): TODO
        lettered (bool): TODO
        caseSensitive (bool): TODO

    Returns the choice selected as it appeared in `choices`. That is, if `'cat'`
    was a choice and the user entered `'CAT'` while caseSensitive is `False`,
    this function will return `'cat'`.
    """

    # Validate parameters.
    _validateParamsFor_validateChoice(choices=choices, blank=blank, strip=strip, whitelistRegexes=None,
        blacklistRegexes=blacklistRegexes, numbered=numbered, lettered=lettered, caseSensitive=caseSensitive)

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
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
        return choices[[choice.upper() for choice in choices].index(value.upper())]

    raise ValidationException(_('%r is not a valid choice.') % (_errstr(value)))


def _validateParamsFor__validateToDateTimeFormat(formats, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)
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
            time.strftime(format)
        except:
            raise PySimpleValidateException('formats argument contains invalid strftime format strings')


def _validateToDateTimeFormat(value, formats, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    # Validate parameters.
    _validateParamsFor__validateToDateTimeFormat(formats, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
    if returnNow:
        return True

    # Validate against the given formats.
    for format in formats:
        try:
            time.strptime(value, format)
        except ValueError:
            continue # If this format fails to parse, move on to the next format.
        return True
    raise ValidationException(_('%r is not a valid time formatted as %s') % (value, time.strftime(formats[0])))


def validateTime(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None,
                 formats=('%H:%M:%S', '%H:%M', '%X')):
    """Returns True if value is a time that passes validation. Raises an
    exception if ValidationException if value fails validation.

    Args:
        value (str): The value being validated as a time.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        whitelistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blacklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid time.
    """

    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        if _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid time formatted as %s') % (_errstr(value), time.strftime(formats[0])))


def validateDate(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None,
                 formats=('%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d', '%y/%m/%d', '%x')):
    """Returns True if value is a date that passes validation. Raises an
    exception if ValidationException if value fails validation.

    Args:
        value (str): The value being validated as a time.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        whitelistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blacklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid date.
    """
    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        if _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid date formatted as %s') % (_errstr(value), time.strftime(formats[0])))


def validateDatetime(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None,
                     formats=('%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S',
                              '%m/%d/%Y %H:%M', '%m/%d/%y %H:%M', '%Y/%m/%d %H:%M', '%y/%m/%d %H:%M', '%x %H:%M',
                              '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S')):
    """Returns True if value is a datetime that passes validation. Raises an
    exception if ValidationException if value fails validation.

    Args:
        value (str): The value being validated as a time.
        blank (bool): If False, a blank string for value will be accepted.
        strip (bool, str, None): If True, whitespace is stripped from value. If a str, the characters in it are stripped from value. If None, nothing is stripped.
        whitelistRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
        blacklistRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
        formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid datetime.
    """

    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        if _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid date and time formatted as %s.') % (_errstr(value), time.strftime(formats[0])))


def validateFilename(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None, mustExist=False):
    # TODO - finish this.
    if value.endswith(' '):
        raise ValidationException(_('%r is not a valid filename because it ends with a space.') % (_errstr(value)))
    raise NotImplementedError()


def validateFilepath(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None, mustExist=False):
    # TODO - finish this.
    raise NotImplementedError()


def validateIpAddr(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    # Reuse the logic in validateRegex()
    try:
        if validateRegex(value=value, regex=IPV4_REGEX, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes):
            return True
        if validateRegex(value=value, regex=IPV6_REGEX, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid IP address.') % (_errstr(value)))


def _validateParamsFor_validateRegex(blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)


def validateRegex(value, regex='', flags=0, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    # Validate parameters.
    _validateParamsFor_validateRegex(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
    if returnNow:
        return True

    if re.compile(regex, flags).search(value) is not None:
        return True
    else:
        raise ValidationException(_('%r does not match the specified pattern.') % (_errstr(value)))


def _validateParamsFor_validateLiteralRegex(blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)


def validateLiteralRegex(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    # TODO - I'd be nice to check regexes in other languages, i.e. JS and Perl.
    _validateParamsFor_validateRegex(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
    if returnNow:
        return True

    try:
        re.compile(value)
    except Exception as ex:
        raise ValidationException(_('%r is not a valid regular expression: %s') % (_errstr(value), ex))


def validateURL(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    # Reuse the logic in validateRege()
    try:
        if validateRegex(value=value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid URL.') % (value))


def validateYesNo(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None, yes='yes', no='no', caseSensitive=False):

    # Note: Rather than always return True, this function returns the original `yes` or `no` argument, depending on what `value` represents.

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    yes = str(yes)
    no = str(no)
    if len(yes) == 0:
        raise PySimpleValidateException('yes argument must be a non-empty string.')
    if len(no) == 0:
        raise PySimpleValidateException('no argument must be a non-empty string.')

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
    if returnNow:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    if caseSensitive:
        if value in (yes, yes[0]):
            return yes
        elif value in (no, no[0]):
            return no
    else:
        if value in (yes.upper(), yes[0].upper()):
            return yes
        elif value in (no.upper(), no[0].upper()):
            return no

    raise ValidationException(_('%r is not a valid %s/%s response.') % (_errstr(value), yes, no))



def validateName():
    raise NotImplementedError()


def validateAddress():
    raise NotImplementedError()


def validateState(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None, caseSensitive=False):
    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
    if returnNow:
        return True

    if caseSensitive:
        if value in STATES:
            return True
    else:
        if value.upper() in STATES_UPPER:
            return True

    raise ValidationException(_('%r is not a state.') % (_errstr(value)))


def validateZipCode(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None):
    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, whitelistRegexes, blacklistRegexes)
    if returnNow:
        return True

    try:
        int(value)
    except ValueError:
        raise ValidationException(_('%r is not a zip code.') % (value))

    if 100 < int(value) < 99999:
        return True
    else:
        raise ValidationException(_('%r is not a zip code.') % (value))


def validatePhone():
    raise NotImplementedError()


def validateMonth(value, blank=False, strip=True, whitelistRegexes=None, blacklistRegexes=None, caseSensitive=False,
                  monthNames=MONTHS):
    # TODO - accept abbreviated forms and numbered months as well.
    raise NotImplementedError()


def validateDayOfWeek():
    # TODO - reuse validateChoice for this function
    raise NotImplementedError()


def validateDayOfMonth():
    # TODO - reuse validateChoice for this function
    raise NotImplementedError()


def validateYear():
    # TODO - reuse validateInt for this function
    raise NotImplementedError()
