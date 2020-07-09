# PySimpleValidate
# By Al Sweigart al@inventwithpython.com

from __future__ import absolute_import, division, print_function

import calendar
import datetime
import re
import sys
import time

from typing import Union, Pattern, Type, Dict, Tuple, Optional, Sequence, Any, List


__version__ = "0.2.12"  # type: str

# In Python 3, regex pattern classes are re.Pattern
# In Python 2, regex pattern classes are SRE_Pattern but there's no exposed class that I can pass to isinstance.
RE_PATTERN_TYPE = type(re.compile(""))

if sys.version_info >= (3, 3):
    import collections.abc

    SEQUENCE_ABC = collections.abc.Sequence
else:
    import collections

    SEQUENCE_ABC = collections.Sequence

# Used by _errstr():
MAX_ERROR_STR_LEN = 50  # type: int

# From https://stackoverflow.com/a/5284410/1893164
IPV4_REGEX = re.compile(r"""((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}""")  # type: Pattern

REGEX_TYPE = type(IPV4_REGEX)  # type: Type

# From https://stackoverflow.com/a/17871737/1893164
IPV6_REGEX = re.compile(
    r"""(
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
)""",
    re.VERBOSE,
)  # type: Pattern

URL_REGEX = re.compile(
    r"""(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"""
)  # type: Pattern

# https://emailregex.com/
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")  # type: Pattern

# TODO - make STATES a dictionary mapping abbreviation to full name
USA_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}  # type: Dict[str, str]
USA_STATES_REVERSED = dict([(USA_STATES[abbrev], abbrev) for abbrev in USA_STATES.keys()])  # type: Dict[str, str]
USA_STATES_UPPER = dict([(abbrev, USA_STATES[abbrev].upper()) for abbrev in USA_STATES.keys()])  # type: Dict[str, str]

ENGLISH_MONTHS = {
    "JAN": "January",
    "FEB": "February",
    "MAR": "March",
    "APR": "April",
    "MAY": "May",
    "JUN": "June",
    "JUL": "July",
    "AUG": "August",
    "SEP": "September",
    "OCT": "October",
    "NOV": "November",
    "DEC": "December",
}  # type: Dict[str, str]

ENGLISH_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)  # type: Tuple[str, str, str, str, str, str, str, str, str, str, str, str]

ENGLISH_DAYS_OF_WEEK = {
    "SUN": "Sunday",
    "MON": "Monday",
    "TUE": "Tuesday",
    "WED": "Wednesday",
    "THU": "Thursday",
    "FRI": "Friday",
    "SAT": "Saturday",
}  # type: Dict[str, str]

DEFAULT_BLOCKLIST_RESPONSE = "This response is invalid."  # type: str


class PySimpleValidateException(Exception):
    """Base class for exceptions raised when PySimpleValidate functions are misused.
    This doesn't represent a validation failure."""

    pass


class ValidationException(Exception):
    """Raised when a validation function fails to validate the value."""

    pass


def _(s):
    # type: (str) -> str
    """This function is a stub for implementing gettext and I18N for PySimpleValidate."""
    return s


def _errstr(value):
    # type: (str) -> str
    """Returns the value str, truncated to MAX_ERROR_STR_LEN characters. If
    it's truncated, the returned value will have '...' on the end.
    """
    # We won't make the caller convert value to a string each time.
    value = str(value)
    if len(value) > MAX_ERROR_STR_LEN:
        return value[:MAX_ERROR_STR_LEN] + "..."
    else:
        return value


def _getStrippedValue(value, strip):
    # type: (str, Union[None, str, bool]) -> str
    """Like the strip() string method, except the strip argument describes
    different behavior:

    If strip is None, whitespace is stripped.

    If strip is a string, the characters in the string are stripped.

    If strip is False, nothing is stripped."""
    if strip is None:
        value = value.strip()  # Call strip() with no arguments to strip whitespace.
    elif isinstance(strip, str):
        value = value.strip(strip)  # Call strip(), passing the strip argument.
    elif strip is False:
        pass  # Don't strip anything.
    return value


def _raiseValidationException(standardExcMsg, customExcMsg=None):
    # type: (str, Optional[str]) -> None
    """Raise ValidationException with standardExcMsg, unless customExcMsg is specified."""
    if customExcMsg is None:
        raise ValidationException(str(standardExcMsg))
    else:
        raise ValidationException(str(customExcMsg))


def _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> Tuple[bool, str]
    """Returns a tuple of two values: the first is a bool that tells the caller
    if they should immediately return True, the second is a new, possibly stripped
    value to replace the value passed for value parameter.

    We'd want the caller immediately return value in some cases where further
    validation isn't needed, such as if value is blank and blanks are
    allowed, or if value matches an allowlist or blocklist regex.

    This function is called by the validate*() functions to perform some common
    housekeeping."""

    # TODO - add a allowlistFirst and blocklistFirst to determine which is checked first. (Right now it's allowlist)

    value = str(value)

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    # Validate for blank values.
    if not blank and value == "":
        # value is blank but blanks aren't allowed.
        _raiseValidationException(_("Blank values are not allowed."), excMsg)
    elif blank and value == "":
        return (
            True,
            value,
        )  # The value is blank and blanks are allowed, so return True to indicate that the caller should return value immediately.

    # NOTE: We check if something matches the allow-list first, then we check the block-list second.

    # Check the allowRegexes.
    if allowRegexes is not None:
        for allowRegex in allowRegexes:
            if isinstance(allowRegex, RE_PATTERN_TYPE):
                if allowRegex.search(value) is not None:
                    return (
                        True,
                        value,
                    )  # The value is in the allowlist, so return True to indicate that the caller should return value immediately.
            else:
                if re.search(allowRegex, value) is not None:
                    return (
                        True,
                        value,
                    )  # The value is in the allowlist, so return True to indicate that the caller should return value immediately.

    # Check the blockRegexes.
    if blockRegexes is not None:
        for blocklistRegexItem in blockRegexes:
            if isinstance(blocklistRegexItem, (str, RE_PATTERN_TYPE)):
                regex, response = blocklistRegexItem, DEFAULT_BLOCKLIST_RESPONSE
            else:
                # NOTE: blockRegexes is potentially so many types at runtime, so ignore the type hint error on this next line:
                regex, response = blocklistRegexItem  # type: ignore

            if isinstance(regex, RE_PATTERN_TYPE) and regex.search(value) is not None:
                _raiseValidationException(response, excMsg)  # value is on a blocklist
            elif re.search(regex, value) is not None:
                _raiseValidationException(response, excMsg)  # value is on a blocklist

    return (
        False,
        value,
    )  # Return False and the possibly modified value, and leave it up to the caller to decide if it's valid or not.


def _validateGenericParameters(blank, strip, allowRegexes, blockRegexes):
    # type: (bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]]) -> None
    """Returns None if the blank, strip, and blockRegexes parameters are valid
    of PySimpleValidate's validation functions have. Raises a PySimpleValidateException
    if any of the arguments are invalid."""

    # Check blank parameter.
    if not isinstance(blank, bool):
        raise PySimpleValidateException("blank argument must be a bool")

    # Check strip parameter.
    if not isinstance(strip, (bool, str, type(None))):
        raise PySimpleValidateException("strip argument must be a bool, None, or str")

    # Check allowRegexes parameter (including each regex in it).
    if allowRegexes is None:
        allowRegexes = []  # allowRegexes defaults to a blank list.

    if not isinstance(allowRegexes, SEQUENCE_ABC):
        raise PySimpleValidateException("allowRegexes must be a sequence of regex_strs")

    for allowRegex in allowRegexes:
        if not isinstance(allowRegex, (str, RE_PATTERN_TYPE)):
            raise PySimpleValidateException("items in allowRegexes must be a regex pattern or regex str")

    # Check allowRegexes parameter (including each regex in it).
    # NOTE: blockRegexes is NOT the same format as allowlistRegex, it can
    # include an "invalid input reason" string to display if the input matches
    # the blocklist regex.
    if blockRegexes is None:
        blockRegexes = []  # blockRegexes defaults to a blank list.

    if not isinstance(blockRegexes, SEQUENCE_ABC):
        raise PySimpleValidateException(
            "blockRegexes must be a pattern, regex str, or sequence of (pattern, regex str) tuples"
        )
    for blockRegex in blockRegexes:
        if isinstance(blockRegex, (str, RE_PATTERN_TYPE)):
            continue
        # NOTE: blockRegex is potentially so many types at runtime, so ignore the type hint error on this next line:
        if len(blockRegex) != 2:  # type: ignore
            raise PySimpleValidateException(
                "blockRegexes must be a pattern, regex str, or sequence of (pattern, regex str) tuples"
            )
        if not isinstance(blockRegex[0], str) or not isinstance(blockRegex[1], str):  # type: ignore
            raise PySimpleValidateException(
                "blockRegexes must be a pattern, regex str, or sequence of (pattern, regex str) tuples"
            )


def _validateParamsFor_validateNum(min=None, max=None, lessThan=None, greaterThan=None):
    # type: (Union[int, float, None], Union[int, float, None], Union[int, float, None], Union[int, float, None]) -> None
    """Raises an exception if the arguments are invalid. This is called by
    the validateNum(), validateInt(), and validateFloat() functions to
    check its arguments. This code was refactored out to a separate function
    so that the PyInputPlus module (or other modules) could check their
    parameters' arguments for inputNum() etc.
    """

    if (min is not None) and (greaterThan is not None):
        raise PySimpleValidateException("only one argument for min or greaterThan can be passed, not both")
    if (max is not None) and (lessThan is not None):
        raise PySimpleValidateException("only one argument for max or lessThan can be passed, not both")

    if (min is not None) and (max is not None) and (min > max):
        raise PySimpleValidateException("the min argument must be less than or equal to the max argument")
    if (min is not None) and (lessThan is not None) and (min >= lessThan):
        raise PySimpleValidateException("the min argument must be less than the lessThan argument")
    if (max is not None) and (greaterThan is not None) and (max <= greaterThan):
        raise PySimpleValidateException("the max argument must be greater than the greaterThan argument")

    for name, val in (("min", min), ("max", max), ("lessThan", lessThan), ("greaterThan", greaterThan)):
        if not isinstance(val, (int, float, type(None))):
            raise PySimpleValidateException(name + " argument must be int, float, or NoneType")


def validateStr(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value is not a string. This function
    is identical to the built-in input() function, but also offers the
    PySimpleValidate features of not allowing blank values by default,
    automatically stripping whitespace, and having allowlist/blocklist
    regular expressions.

    Returns value, so it can be used inline in an expression:

        print('Hello, ' + validateStr(your_name))

    * value (str): The value being validated as a string.
    * blank (bool): If True, a blank string will be accepted. Defaults to False. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateStr('hello')
    'hello'
    >>> pysv.validateStr('')
    Traceback (most recent call last):
      ...
    pysimplevalidate.ValidationException: Blank values are not allowed.
    >>> pysv.validateStr('', blank=True)
    ''
    >>> pysv.validateStr('    hello    ')
    'hello'
    >>> pysv.validateStr('hello', blockRegexes=['hello'])
    Traceback (most recent call last):
      ...
    pysimplevalidate.ValidationException: This response is invalid.
    >>> pysv.validateStr('hello', blockRegexes=[('hello', 'Hello is not allowed')])
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: Hello is not allowed
    >>> pysv.validateStr('hello', allowRegexes=['hello'], blockRegexes=['llo'])
    'hello'
    """

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=None, blockRegexes=blockRegexes)
    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)

    return value


def validateNum(
    value,
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    _numType="num",
    min=None,
    max=None,
    lessThan=None,
    greaterThan=None,
    excMsg=None,
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], str, Optional[int], Optional[int], Optional[int], Optional[int], Optional[str]) -> Union[int, float, str]
    """Raises ValidationException if value is not a float or int.

    Returns value, so it can be used inline in an expression:

        print(2 + validateNum(your_number))

    Note that since int() and float() ignore leading or trailing whitespace
    when converting a string to a number, so does this validateNum().

    * value (str): The value being validated as an int or float.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
    * min (int, float): The (inclusive) minimum value for the value to pass validation.
    * max (int, float): The (inclusive) maximum value for the value to pass validation.
    * lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
    * greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    If you specify min or max, you cannot also respectively specify lessThan
    or greaterThan. Doing so will raise PySimpleValidateException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateNum('3')
    3
    >>> pysv.validateNum('3.0')
    3.0
    >>> pysv.validateNum('    3.0    ')
    3.0
    >>> pysv.validateNum('549873259847598437598435798435793.589985743957435794357')
    5.498732598475984e+32
    >>> pysv.validateNum('4', lessThan=4)
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: Number must be less than 4.
    >>> pysv.validateNum('4', max=4)
    4
    >>> pysv.validateNum('4', min=2, max=5)
    4
    """

    # TODO - Add notes to the documentation that the parameters (except value) should all be passed using keyword arguments.

    assert _numType in ("num", "int", "float")

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=None, blockRegexes=blockRegexes)
    _validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        # If we can convert value to an int/float, then do so. For example,
        # if an allowlist regex allows '42', then we should return 42 or 42.0.
        if (_numType == "num" and "." in value) or (_numType == "float"):
            try:
                return float(value)
            except ValueError:
                return value  # Return the value as is.
        elif (_numType == "num" and "." not in value) or (_numType == "int"):
            try:
                return int(value)
            except ValueError:
                return value  # Return the value as is.
        else:
            assert False  # This branch should never happen.

    # Validate the value's type (and convert value back to a number type).
    if _numType == "num" and "." in value:
        # We are expecting a "num" (float or int) type and the user entered a float.
        try:
            numericValue = float(value)  # type: Union[int, float]
        except:
            _raiseValidationException(_("%r is not a number.") % (_errstr(value)), excMsg)
    elif _numType == "num" and "." not in value:
        # We are expecting a "num" (float or int) type and the user entered an int.
        try:
            numericValue = int(value)
        except:
            _raiseValidationException(_("%r is not a number.") % (_errstr(value)), excMsg)
    elif _numType == "float":
        try:
            numericValue = float(value)
        except:
            _raiseValidationException(_("%r is not a float.") % (_errstr(value)), excMsg)
    elif _numType == "int":
        try:
            if float(value) % 1 != 0:
                # The number is a float that doesn't end with ".0"
                _raiseValidationException(_("%r is not an integer.") % (_errstr(value)), excMsg)
            numericValue = int(float(value))
        except:
            _raiseValidationException(_("%r is not an integer.") % (_errstr(value)), excMsg)
    else:
        assert False  # This branch should never happen.

    # Validate against min argument.
    if min is not None and numericValue < min:
        _raiseValidationException(_("Number must be at minimum %s.") % (min), excMsg)

    # Validate against max argument.
    if max is not None and numericValue > max:
        _raiseValidationException(_("Number must be at maximum %s.") % (max), excMsg)

    # Validate against max argument.
    if lessThan is not None and numericValue >= lessThan:
        _raiseValidationException(_("Number must be less than %s.") % (lessThan), excMsg)

    # Validate against max argument.
    if greaterThan is not None and numericValue <= greaterThan:
        _raiseValidationException(_("Number must be greater than %s.") % (greaterThan), excMsg)

    return numericValue


def validateInt(
    value,
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    min=None,
    max=None,
    lessThan=None,
    greaterThan=None,
    excMsg=None,
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[int], Optional[int], Optional[int], Optional[int], Optional[str]) -> Union[int, str]
    """Raises ValidationException if value is not a int.

    Returns value, so it can be used inline in an expression:

        print(2 + validateInt(your_number))

    Note that since int() and ignore leading or trailing whitespace
    when converting a string to a number, so does this validateNum().

    * value (str): The value being validated as an int or float.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
    * min (int, float): The (inclusive) minimum value for the value to pass validation.
    * max (int, float): The (inclusive) maximum value for the value to pass validation.
    * lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
    * greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    If you specify min or max, you cannot also respectively specify lessThan
    or greaterThan. Doing so will raise PySimpleValidateException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateInt('42')
    42
    >>> pysv.validateInt('forty two')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'forty two' is not an integer.
    """

    # Even though validateNum *could* return a float, it won't if _numType is 'int', so ignore mypy's complaint:
    return validateNum(
        value=value,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,  # type: ignore
        blockRegexes=blockRegexes,
        _numType="int",
        min=min,
        max=max,
        lessThan=lessThan,
        greaterThan=greaterThan,
    )


def validateFloat(
    value,
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    min=None,
    max=None,
    lessThan=None,
    greaterThan=None,
    excMsg=None,
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[int], Optional[int], Optional[int], Optional[int], Optional[str]) -> Union[float, str]
    """Raises ValidationException if value is not a float.

    Returns value, so it can be used inline in an expression:

        print(2 + validateFloat(your_number))

    Note that since float() ignore leading or trailing whitespace
    when converting a string to a number, so does this validateNum().

    * value (str): The value being validated as an int or float.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * _numType (str): One of 'num', 'int', or 'float' for the kind of number to validate against, where 'num' means int or float.
    * min (int, float): The (inclusive) minimum value for the value to pass validation.
    * max (int, float): The (inclusive) maximum value for the value to pass validation.
    * lessThan (int, float): The (exclusive) minimum value for the value to pass validation.
    * greaterThan (int, float): The (exclusive) maximum value for the value to pass validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    If you specify min or max, you cannot also respectively specify lessThan
    or greaterThan. Doing so will raise PySimpleValidateException.

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
    pysimplevalidate.ValidationException: Number must be greater than 3.
    """

    # Even though validateNum *could* return a int, it won't if _numType is 'float', so ignore mypy's complaint:
    return validateNum(
        value=value,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        _numType="float",
        min=min,
        max=max,
        lessThan=lessThan,
        greaterThan=greaterThan,
    )


def _validateParamsFor_validateChoice(
    choices,
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    numbered=False,
    lettered=False,
    caseSensitive=False,
    excMsg=None,
):
    # type: (Sequence[Any], bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], bool, bool, bool, Optional[str]) -> None
    """Raises PySimpleValidateException if the arguments are invalid. This is called by
    the validateChoice() function to check its arguments. This code was
    refactored out to a separate function so that the PyInputPlus module (or
    other modules) could check their parameters' arguments for inputChoice().
    """

    if not isinstance(caseSensitive, bool):
        raise PySimpleValidateException("caseSensitive argument must be a bool")

    if not isinstance(choices, SEQUENCE_ABC):
        raise PySimpleValidateException("choices arg must be a sequence")

    try:
        len(choices)
    except:
        raise PySimpleValidateException("choices arg must be a sequence")
    if blank == False and len(choices) < 2:
        raise PySimpleValidateException("choices must have at least two items if blank is False")
    elif blank == True and len(choices) < 1:
        raise PySimpleValidateException("choices must have at least one item")

    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=None, blockRegexes=blockRegexes)

    if lettered and len(choices) > 26:
        raise PySimpleValidateException("lettered argument cannot be True if there are more than 26 choices")
    if numbered and lettered:
        raise PySimpleValidateException("numbered and lettered arguments cannot both be True")

    if len(choices) != len(set(choices)):
        raise PySimpleValidateException("duplicate entries in choices argument")

    if not caseSensitive and len(choices) != len(set([choice.upper() for choice in choices])):
        raise PySimpleValidateException("duplicate case-insensitive entries in choices argument")


def validateChoice(
    value,
    choices,
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    numbered=False,
    lettered=False,
    caseSensitive=False,
    excMsg=None,
):
    # type: (str, Sequence[Any], bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], bool, bool, bool, Optional[str]) -> str
    """Raises ValidationException if value is not one of the values in
    choices. Returns the selected choice.

    Returns the value in choices that was selected, so it can be used inline
    in an expression:

        print('You chose ' + validateChoice(your_choice, ['cat', 'dog']))

    Note that value itself is not returned: validateChoice('CAT', ['cat', 'dog'])
    will return 'cat', not 'CAT'.

    If lettered is True, lower or uppercase letters will be accepted regardless
    of what caseSensitive is set to. The caseSensitive argument only matters
    for matching with the text of the strings in choices.

    * value (str): The value being validated.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * numbered (bool): If True, this function will also accept a string of the choice's number, i.e. '1' or '2'.
    * lettered (bool): If True, this function will also accept a string of the choice's letter, i.e. 'A' or 'B' or 'a' or 'b'.
    * caseSensitive (bool): If True, then the exact case of the option must be entered.
    * excMsg (str): A custom message to use in the raised ValidationException.

    Returns the choice selected as it appeared in choices. That is, if 'cat'
    was a choice and the user entered 'CAT' while caseSensitive is False,
    this function will return 'cat'.


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
    _validateParamsFor_validateChoice(
        choices=choices,
        blank=blank,
        strip=strip,
        allowRegexes=None,
        blockRegexes=blockRegexes,
        numbered=numbered,
        lettered=lettered,
        caseSensitive=caseSensitive,
    )

    strChoices = []  # type: List[str]
    for choice in choices:
        strChoices.append(str(choice))

    if "" in strChoices:
        # blank needs to be set to True here, otherwise '' won't be accepted as a choice.
        blank = True

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    # Validate against strChoices.
    if value in strChoices:
        return value
    if numbered and value.isdigit() and 0 < int(value) <= len(strChoices):  # value must be 1 to len(strChoices)
        # Numbered options begins at 1, not 0.
        return strChoices[
            int(value) - 1
        ]  # -1 because the numbers are 1 to len(strChoices) but the index are 0 to len(strChoices) - 1
    if lettered and len(value) == 1 and value.isalpha() and 0 < ord(value.upper()) - 64 <= len(strChoices):
        # Lettered options are always case-insensitive.
        return strChoices[ord(value.upper()) - 65]
    if not caseSensitive and value.upper() in [choice.upper() for choice in strChoices]:
        # Return the original item in strChoices that value has a case-insensitive match with.
        return strChoices[[choice.upper() for choice in strChoices].index(value.upper())]

    _raiseValidationException(_("%r is not a valid choice.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def _validateParamsFor__validateToDateTimeFormat(
    formats, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None
):
    # type: (Union[str, Sequence[str]], bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> None
    """Raises PySimpleValidateException if the arguments are invalid. This is called by
    the validateTime() function to check its arguments. This code was
    refactored out to a separate function so that the PyInputPlus module (or
    other modules) could check their parameters' arguments for inputTime().
    """
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)
    if formats is None:
        raise PySimpleValidateException("formats parameter must be specified")

    if isinstance(formats, str):
        raise PySimpleValidateException("formats argument must be a non-str sequence of strftime format strings")

    if not isinstance(formats, SEQUENCE_ABC):
        raise PySimpleValidateException("formats argument must be a non-str sequence of strftime format strings")

    for timeFormat in formats:  # "format" name is used by the built-in format() function, so we use timeFormat instead.
        try:
            time.strftime(timeFormat)  # This will raise an exception if the format is invalid.
        except:
            raise PySimpleValidateException("formats argument contains invalid strftime format strings")


def _validateToDateTimeFormat(
    value, formats, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None
):
    # type: (str, Union[str, Sequence[str]], bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> Union[datetime.datetime, str]
    # Validate parameters.
    _validateParamsFor__validateToDateTimeFormat(
        formats, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes
    )

    if isinstance(formats, str):
        # Ensure that `formats` is always a sequence of strings:
        formats = [formats]

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        for timeFormat in formats:
            # If value can be converted to a datetime object, convert it.
            try:
                return datetime.datetime.strptime(value, timeFormat)
            except ValueError:
                continue  # If this format fails to parse, move on to the next format.
        return value  # Return the value as is.

    # Validate against the given formats.
    for timeFormat in formats:
        try:
            return datetime.datetime.strptime(value, timeFormat)
        except ValueError:
            continue  # If this format fails to parse, move on to the next format.

    _raiseValidationException(_("%r is not a valid time.") % (value), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateTime(
    value,
    formats=("%H:%M:%S", "%H:%M", "%X"),
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    excMsg=None,
):
    # type: (str, Union[str, Sequence[str]], bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> Union[datetime.time, str]
    """Raises ValidationException if value is not a time formatted in one
    of the formats formats. Returns a datetime.time object of value.

    * value (str): The value being validated as a time.
    * formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid time.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateTime('12:00:01')
    datetime.time(12, 0, 1)
    >>> pysv.validateTime('13:00:01')
    datetime.time(13, 0, 1)
    >>> pysv.validateTime('25:00:01')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '25:00:01' is not a valid time.
    >>> pysv.validateTime('hour 12 minute 01', formats=['hour %H minute %M'])
    datetime.time(12, 1)
    """

    # TODO - handle this

    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        dt = _validateToDateTimeFormat(
            value, formats, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid time.") % (_errstr(value)), excMsg)

    # `dt` could be a str if `value` matched one of the `allowRegexes`.
    if isinstance(dt, str):
        return dt  # Return the string value as-is.
    # At this point, dt is definitely a time object, so ignore mypy's complaints:
    return datetime.time(dt.hour, dt.minute, dt.second, dt.microsecond)  # type: ignore


def validateDate(
    value,
    formats=("%Y/%m/%d", "%y/%m/%d", "%m/%d/%Y", "%m/%d/%y", "%x"),
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    excMsg=None,
):
    # type: (str, Union[str, Sequence[str]], bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> Union[datetime.date, str]
    """Raises ValidationException if value is not a time formatted in one
    of the formats formats. Returns a datetime.date object of value.

    * value (str): The value being validated as a time.
    * blank (bool): If True, a blank string for value will be accepted.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid date.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateDate('2/29/2004')
    datetime.date(2004, 2, 29)
    >>> pysv.validateDate('2/29/2005')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '2/29/2005' is not a valid date.
    >>> pysv.validateDate('September 2019', formats=['%B %Y'])
    datetime.date(2019, 9, 1)
    """
    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        dt = _validateToDateTimeFormat(
            value, formats, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid date.") % (_errstr(value)), excMsg)

    # `dt` could be a str if `value` matched one of the `allowRegexes`.
    if isinstance(dt, str):
        return dt  # Return the string value as-is.
    # At this point, dt is definitely a date object, so ignore mypy's complaints:
    return datetime.date(dt.year, dt.month, dt.day)  # type: ignore


def validateDatetime(
    value,
    formats=(
        "%Y/%m/%d %H:%M:%S",
        "%y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
        "%x %H:%M:%S",  # type: ignore
        "%Y/%m/%d %H:%M",
        "%y/%m/%d %H:%M",
        "%m/%d/%Y %H:%M",
        "%m/%d/%y %H:%M",
        "%x %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
        "%x %H:%M:%S",
    ),
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    excMsg=None,
):
    # type: (str, Union[str, Sequence[str]], bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> Union[datetime.datetime, str]
    """Raises ValidationException if value is not a datetime formatted in one
    of the formats formats. Returns a datetime.datetime object of value.

    * value (str): The value being validated as a datetime.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * formats: A tuple of strings that can be passed to time.strftime, dictating the possible formats for a valid datetime.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateDatetime('2018/10/31 12:00:01')
    datetime.datetime(2018, 10, 31, 12, 0, 1)
    >>> pysv.validateDatetime('10/31/2018 12:00:01')
    datetime.datetime(2018, 10, 31, 12, 0, 1)
    >>> pysv.validateDatetime('10/31/2018')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '10/31/2018' is not a valid date and time.
    """

    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        return _validateToDateTimeFormat(
            value, formats, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid date and time.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateFilename(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value is not a valid filename.
    Filenames can't contain \\ / : * ? " < > | or end with a space.
    Returns the value argument.

    Note that this validates filenames, not filepaths. The / and \\ characters
    are invalid for filenames.

    * value (str): The value being validated as an IP address.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateFilename('foobar.txt')
    'foobar.txt'
    >>> pysv.validateFilename('???.exe')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '???.exe' is not a valid filename.
    >>> pysv.validateFilename('/full/path/to/foo.txt')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '/full/path/to/foo.txt' is not a valid filename.
    """

    # TODO: Did I capture the Linux/macOS invalid file characters too, or just Windows's?

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    if (value != value.strip()) or (any(c in value for c in '\\/:*?"<>|')):
        _raiseValidationException(_("%r is not a valid filename.") % (_errstr(value)), excMsg)
    return value


def validateFilepath(
    value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None, mustExist=False
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str], bool) -> str
    r"""Raises ValidationException if value is not a valid filename.
    Filenames can't contain \\ / : * ? " < > |
    Returns the value argument.

    * value (str): The value being validated as an IP address.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateFilepath('foo.txt')
    'foo.txt'
    >>> pysv.validateFilepath('/spam/foo.txt')
    '/spam/foo.txt'
    >>> pysv.validateFilepath(r'c:\spam\foo.txt')
    'c:\\spam\\foo.txt'
    >>> pysv.validateFilepath(r'c:\spam\???.txt')
    Traceback (most recent call last):
      ...
    pysimplevalidate.ValidationException: 'c:\\spam\\???.txt' is not a valid file path.
    """
    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    if (value != value.strip()) or (
        any(c in value for c in '*?"<>|')
    ):  # Same as validateFilename, except we allow \ and / and :
        if ":" in value:
            if value.find(":", 2) != -1 or not value[0].isalpha():
                # For Windows: Colon can only be found at the beginning, e.g. 'C:\', or the first letter is not a letter drive.
                _raiseValidationException(_("%r is not a valid file path.") % (_errstr(value)), excMsg)
        _raiseValidationException(_("%r is not a valid file path.") % (_errstr(value)), excMsg)
    return value
    raise NotImplementedError()


def validateIP(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value is not an IPv4 or IPv6 address.
    Returns the value argument.

    * value (str): The value being validated as an IP address.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateIP('127.0.0.1')
    '127.0.0.1'
    >>> pysv.validateIP('255.255.255.255')
    '255.255.255.255'
    >>> pysv.validateIP('256.256.256.256')
    Traceback (most recent call last):
    pysimplevalidate.ValidationException: '256.256.256.256' is not a valid IP address.
    >>> pysv.validateIP('1:2:3:4:5:6:7:8')
    '1:2:3:4:5:6:7:8'
    >>> pysv.validateIP('1::8')
    '1::8'
    >>> pysv.validateIP('fe80::7:8%eth0')
    'fe80::7:8%eth0'
    >>> pysv.validateIP('::255.255.255.255')
    '::255.255.255.255'
    """
    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    # Reuse the logic in validateRegex()
    try:
        try:
            # Check if value is an IPv4 address.
            return validateRegex(
                value=value,
                regex=IPV4_REGEX,
                blank=blank,
                strip=strip,
                allowRegexes=allowRegexes,
                blockRegexes=blockRegexes,
            )
        except:
            pass  # Go on to check if it's an IPv6 address.

        # Check if value is an IPv6 address.
        return validateRegex(
            value=value,
            regex=IPV6_REGEX,
            blank=blank,
            strip=strip,
            allowRegexes=allowRegexes,
            blockRegexes=blockRegexes,
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid IP address.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateIPv4(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value is not an IPv4 address.
    Returns the value argument.

    * value (str): The value being validated as an IPv4 address.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateIPv4('127.0.0.1')
    '127.0.0.1'
    >>> pysv.validateIPv4('255.255.255.255')
    '255.255.255.255'
    >>> pysv.validateIPv4('256.256.256.256')
    Traceback (most recent call last):
    pysimplevalidate.ValidationException: '256.256.256.256' is not a valid IP address.
    """

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    # Reuse the logic in validateRegex()

    try:
        # Check if value is an IPv4 address.
        return validateRegex(
            value=value,
            regex=IPV4_REGEX,
            blank=blank,
            strip=strip,
            allowRegexes=allowRegexes,
            blockRegexes=blockRegexes,
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid IPv4 address.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateIPv6(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value is not an IPv6 address.
    Returns the value argument.

    * value (str): The value being validated as an IPv6 address.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateIP('1:2:3:4:5:6:7:8')
    '1:2:3:4:5:6:7:8'
    >>> pysv.validateIP('1::8')
    '1::8'
    >>> pysv.validateIP('fe80::7:8%eth0')
    'fe80::7:8%eth0'
    >>> pysv.validateIP('::255.255.255.255')
    '::255.255.255.255'
    """
    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    # Reuse the logic in validateRegex()
    try:
        # Check if value is an IPv6 address.
        return validateRegex(
            value=value,
            regex=IPV6_REGEX,
            blank=blank,
            strip=strip,
            allowRegexes=allowRegexes,
            blockRegexes=blockRegexes,
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid IPv6 address.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateRegex(value, regex, flags=0, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, Union[str, Pattern], int, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value does not match the regular expression in regex.
    Returns the value argument.

    This is similar to calling inputStr() and using the allowRegexes
    keyword argument, however, validateRegex() allows you to pass regex
    flags such as re.IGNORECASE or re.VERBOSE. You can also pass a regex
    object directly.

    If you want to check if a string is a regular expression string, call
    validateRegexStr().

    * value (str): The value being validated as a regular expression string.
    * regex (str, regex): The regular expression to match the value against.
    * flags (int): Identical to the flags argument in re.compile(). Pass re.VERBOSE et al here.
    * blank (bool): If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> pysv.validateRegex('cat bat rat', r'(cat)|(dog)|(moose)', re.IGNORECASE)
    'cat'
    >>> pysv.validateRegex('He said "Hello".', r'"(.*?)"', re.IGNORECASE)
    '"Hello"'
    """

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    # Search value with regex, whether regex is a str or regex object.
    if isinstance(regex, str):
        # TODO - check flags to see they're valid regex flags.
        mo = re.compile(regex, flags).search(value)
    elif isinstance(regex, REGEX_TYPE):
        mo = regex.search(value)
    else:
        raise PySimpleValidateException("regex must be a str or regex object")

    if mo is not None:
        return mo.group()
    else:
        _raiseValidationException(_("%r does not match the specified pattern.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateRegexStr(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> Union[str, Pattern]
    """Raises ValidationException if value can't be used as a regular expression string.
    Returns the value argument as a regex object.

    If you want to check if a string matches a regular expression, call
    validateRegex().

    * value (str): The value being validated as a regular expression string.
    * regex (str, regex): The regular expression to match the value against.
    * flags (int): Identical to the flags argument in re.compile(). Pass re.VERBOSE et al here.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateRegexStr('(cat)|(dog)')
    re.compile('(cat)|(dog)')
    >>> pysv.validateRegexStr('"(.*?)"')
    re.compile('"(.*?)"')
    >>> pysv.validateRegexStr('"(.*?"')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '"(.*?"' is not a valid regular expression: missing ), unterminated subpattern at position 1
    """

    # TODO - I'd be nice to check regexes in other languages, i.e. JS and Perl.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    try:
        return re.compile(value)
    except Exception as ex:
        _raiseValidationException(_("%r is not a valid regular expression: %s") % (_errstr(value), ex), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateURL(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value is not a URL.
    Returns the value argument.

    The "http" or "https" protocol part of the URL is optional.

    * value (str): The value being validated as a URL.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateURL('https://inventwithpython.com')
    'https://inventwithpython.com'
    >>> pysv.validateURL('inventwithpython.com')
    'inventwithpython.com'
    >>> pysv.validateURL('localhost')
    'localhost'
    >>> pysv.validateURL('mailto:al@inventwithpython.com')
    'mailto:al@inventwithpython.com'
    >>> pysv.validateURL('ftp://example.com')
    'example.com'
    >>> pysv.validateURL('https://inventwithpython.com/blog/2018/02/02/how-to-ask-for-programming-help/')
    'https://inventwithpython.com/blog/2018/02/02/how-to-ask-for-programming-help/'
    >>> pysv.validateURL('blah blah blah')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'blah blah blah' is not a valid URL.
    """

    # Reuse the logic in validateRegex()
    try:
        return validateRegex(
            value=value, regex=URL_REGEX, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes
        )
    except ValidationException:
        # 'localhost' is also an acceptable URL:
        if value == "localhost":
            return "localhost"

        _raiseValidationException(_("%r is not a valid URL.") % (value), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateEmail(value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> str
    """Raises ValidationException if value is not an email address.
    Returns the value argument.

    * value (str): The value being validated as an email address.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateEmail('al@inventwithpython.com')
    'al@inventwithpython.com'
    >>> pysv.validateEmail('alinventwithpython.com')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'alinventwithpython.com' is not a valid email address.
    """

    # Reuse the logic in validateRegex()
    try:
        return validateRegex(
            value=value,
            regex=EMAIL_REGEX,
            blank=blank,
            strip=strip,
            allowRegexes=allowRegexes,
            blockRegexes=blockRegexes,
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid email address.") % (value), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateYesNo(
    value,
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    yesVal="yes",
    noVal="no",
    caseSensitive=False,
    excMsg=None,
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], str, str, bool, Optional[str]) -> str
    """Raises ValidationException if value is not a yes or no response.
    Returns the yesVal or noVal argument, not value.

    Note that value can be any case (by default) and can also just match the

    * value (str): The value being validated as an email address.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * caseSensitive (bool): Determines if value must match the case of yesVal and noVal. Defaults to False.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateYesNo('y')
    'yes'
    >>> pysv.validateYesNo('YES')
    'yes'
    >>> pysv.validateYesNo('No')
    'no'
    >>> pysv.validateYesNo('OUI', yesVal='oui', noVal='no')
    'oui'
    """

    # Validate parameters. TODO - can probably improve this to remove the duplication.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    yesVal = str(yesVal)
    noVal = str(noVal)
    if len(yesVal) == 0:
        raise PySimpleValidateException("yesVal argument must be a non-empty string.")
    if len(noVal) == 0:
        raise PySimpleValidateException("noVal argument must be a non-empty string.")
    if (yesVal == noVal) or (not caseSensitive and yesVal.upper() == noVal.upper()):
        raise PySimpleValidateException("yesVal and noVal arguments must be different.")
    if (yesVal[0] == noVal[0]) or (not caseSensitive and yesVal[0].upper() == noVal[0].upper()):
        raise PySimpleValidateException("first character of yesVal and noVal arguments must be different")

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
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

    _raiseValidationException(_("%r is not a valid %s/%s response.") % (_errstr(value), yesVal, noVal), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateBool(
    value,
    blank=False,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    trueVal="True",
    falseVal="False",
    caseSensitive=False,
    excMsg=None,
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], str, str, bool, Optional[str]) -> Union[bool, str]
    """Raises ValidationException if value is not a "true" or "false" value.
    Returns the trueVal or falseVal argument, not value.

    * value (str): The value being validated as an email address.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * trueVal TODO
    * falseVal TODO
    * caseInsensitive TODO
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateYesNo('y')
    'yes'
    >>> pysv.validateYesNo('YES')
    'yes'
    >>> pysv.validateYesNo('No')
    'no'
    >>> pysv.validateYesNo('OUI', yesVal='oui', noVal='no')
    'oui'
    """

    # Validate parameters. TODO - can probably improve this to remove the duplication.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    # Replace the exception messages used in validateYesNo():
    trueVal = str(trueVal)
    falseVal = str(falseVal)
    if len(trueVal) == 0:
        raise PySimpleValidateException("trueVal argument must be a non-empty string.")
    if len(falseVal) == 0:
        raise PySimpleValidateException("falseVal argument must be a non-empty string.")
    if (trueVal == falseVal) or (not caseSensitive and trueVal.upper() == falseVal.upper()):
        raise PySimpleValidateException("trueVal and noVal arguments must be different.")
    if (trueVal[0] == falseVal[0]) or (not caseSensitive and trueVal[0].upper() == falseVal[0].upper()):
        raise PySimpleValidateException("first character of trueVal and noVal arguments must be different")

    try:
        result = validateYesNo(
            value,
            blank=blank,
            strip=strip,
            allowRegexes=allowRegexes,
            blockRegexes=blockRegexes,
            yesVal=trueVal,
            noVal=falseVal,
            caseSensitive=caseSensitive,
            excMsg=None,
        )
    except ValidationException:
        _raiseValidationException(_("%r is not a valid %s/%s response.") % (_errstr(value), trueVal, falseVal), excMsg)

    # Return a bool value instead of a string.
    if result == trueVal:
        return True
    elif result == falseVal:
        return False
    else:
        assert (
            False
        ), "inner validateYesNo() call returned something that was not yesVal or noVal. This should never happen."


def validateUSState(
    value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None, returnStateName=False
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str], bool) -> str
    """Raises ValidationException if value is not a USA state.
    Returns the capitalized state abbreviation, unless returnStateName is True
    in which case it returns the titlecased state name.

    * value (str): The value being validated as an email address.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.
    * returnStateName (bool): If True, the full state name is returned, i.e. 'California'. Otherwise, the abbreviation, i.e. 'CA'. Defaults to False.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateState('tx')
    'TX'
    >>> pysv.validateState('california')
    'CA'
    >>> pysv.validateState('WASHINGTON')
    'WA'
    >>> pysv.validateState('WASHINGTON', returnStateName=True)
    'Washington'
    """

    # TODO - note that this is USA-centric. I should work on trying to make this more international.

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    if value.upper() in USA_STATES_UPPER.keys():  # check if value is a state abbreviation
        if returnStateName:
            return USA_STATES[value.upper()]  # Return full state name.
        else:
            return value.upper()  # Return abbreviation.
    elif value.title() in USA_STATES.values():  # check if value is a state name
        if returnStateName:
            return value.title()  # Return full state name.
        else:
            return USA_STATES_REVERSED[value.title()]  # Return abbreviation.

    _raiseValidationException(_("%r is not a state.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateName():
    raise NotImplementedError()


def validateAddress():
    raise NotImplementedError()


def validatePhone():
    raise NotImplementedError()


def validateMonth(
    value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, monthNames=ENGLISH_MONTHS, excMsg=None
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Dict[str, str], Optional[str]) -> str
    """Raises ValidationException if value is not a month, like 'Jan' or 'March'.
    Returns the titlecased month.

    * value (str): The value being validated as an email address.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * monthNames (Mapping): A mapping of uppercase month abbreviations to month names, i.e. {'JAN': 'January', ... }. The default provides English month names.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateMonth('Jan')
    'January'
    >>> pysv.validateMonth('MARCH')
    'March'
    """

    # returns full month name, e.g. 'January'

    # Validate parameters.
    _validateGenericParameters(blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes)

    returnNow, value = _prevalidationCheck(value, blank, strip, allowRegexes, blockRegexes, excMsg)
    if returnNow:
        return value

    try:
        if (monthNames == ENGLISH_MONTHS) and (
            1 <= int(value) <= 12
        ):  # This check here only applies to months, not when validateDayOfWeek() calls this function.
            return ENGLISH_MONTH_NAMES[int(value) - 1]
    except:
        pass  # continue if the user didn't enter a number 1 to 12.

    # Both month names and month abbreviations will be at least 3 characters.
    if len(value) < 3:
        _raiseValidationException(_("%r is not a month.") % (_errstr(value)), excMsg)

    if value[:3].upper() in monthNames.keys():  # check if value is a month abbreviation
        return monthNames[value[:3].upper()]  # It turns out that titlecase is good for all the month.
    elif value.upper() in monthNames.values():  # check if value is a month name
        return value.title()

    _raiseValidationException(_("%r is not a month.") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateDayOfWeek(
    value, blank=False, strip=None, allowRegexes=None, blockRegexes=None, dayNames=ENGLISH_DAYS_OF_WEEK, excMsg=None
):
    # type: (str, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Dict[str, str], Optional[str]) -> str
    """Raises ValidationException if value is not a day of the week, such as 'Mon' or 'Friday'.
    Returns the titlecased day of the week.

    * value (str): The value being validated as a day of the week.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * dayNames (Mapping): A mapping of uppercase day abbreviations to day names, i.e. {'SUN': 'Sunday', ...} The default provides English day names.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateDayOfWeek('mon')
    'Monday'
    >>> pysv.validateDayOfWeek('THURSday')
    'Thursday'
    """

    # TODO - reuse validateChoice for this function

    # returns full day of the week str, e.g. 'Sunday'

    # Reuses validateMonth.
    try:
        return validateMonth(
            value,
            blank=blank,
            strip=strip,
            allowRegexes=allowRegexes,
            blockRegexes=blockRegexes,
            monthNames=ENGLISH_DAYS_OF_WEEK,
        )
    except:
        # Replace the exception message.
        _raiseValidationException(_("%r is not a day of the week") % (_errstr(value)), excMsg)
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


def validateDayOfMonth(value, year, month, blank=False, strip=None, allowRegexes=None, blockRegexes=None, excMsg=None):
    # type: (str, int, int, bool, Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[str]) -> int
    """Raises ValidationException if value is not a day of the month, from
    1 to 28, 29, 30, or 31 depending on the month and year.
    Returns value.

    * value (str): The value being validated as existing as a numbered day in the given year and month.
    * year (int): The given year.
    * month (int): The given month. 1 is January, 2 is February, and so on.
    * blank (bool):  If True, a blank string will be accepted. Defaults to False.
    * strip (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
    * allowRegexes (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers.
    * blockRegexes (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation.
    * excMsg (str): A custom message to use in the raised ValidationException.

    >>> import pysimplevalidate as pysv
    >>> pysv.validateDayOfMonth('31', 2019, 10)
    31
    >>> pysv.validateDayOfMonth('32', 2019, 10)
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '32' is not a day in the month of October 2019
    >>> pysv.validateDayOfMonth('29', 2004, 2)
    29
    >>> pysv.validateDayOfMonth('29', 2005, 2)
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '29' is not a day in the month of February 2005

    """
    year = int(year)
    month = int(month)
    try:
        daysInMonth = calendar.monthrange(year, month)[1]
    except:
        raise PySimpleValidateException("invalid arguments for year and/or month")

    try:
        return int(
            validateInt(
                value,
                blank=blank,
                strip=strip,
                allowRegexes=allowRegexes,
                blockRegexes=blockRegexes,
                min=1,
                max=daysInMonth,
            )
        )
    except:
        # Replace the exception message.
        _raiseValidationException(
            _("%r is not a day in the month of %s %s") % (_errstr(value), ENGLISH_MONTH_NAMES[month - 1], year), excMsg
        )
    assert False, "The execution reached this point, even though the previous line should have raised an exception."


if __name__ == "__main__":
    pass
    # import doctest
    # doctest.testmod()
