# PySimpleValidate
# By Al Sweigart

# TODO: Add "strict mode"
from __future__ import absolute_import, division, print_function

import re
import time




__version__ = '0.1.0'


MAX_ERROR_STR_LEN = 50


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
    if strip is True:
        value = value.strip() # Call strip() with no arguments to strip whitespace.
    elif strip is not False:
        value = value.strip(strip) # Call strip(), passing the strip argument.
    return value


def _handleBlankValues(value, blank=False, strip=True):
    """Raise a ValidationException if the value is blank and blanks aren't
    allowed. Returns True if value is an empty string and blank is True."""

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    # Validate for blank values.
    if not blank and value == '':
        raise ValidationException(_('Blank values are not allowed.'))
    elif blank and value == '':
        return True
    else:
        return None


def _getBlacklistResponse(value, blacklist):
    """Where blacklist is a list of ('regex', 'response') tuples, this function
    returns the first response string whose regex matches value. Returns None
    if the value matches none of the regexes."""

    # NOTE: blacklist is not validated in this private function.

    if blacklist is None:
        return None

    for regex, response in blacklist:
        mo = re.compile(regex).search(value)
        if mo is not None:
            # Return the response that matches this regex.
            return response
    return None


def _validateGenericParameters(blank, strip, blacklist):
    """Returns None if the blank, strip, and blacklist parameters that all
    of PySimpleValidate's validation functions have. Raises a PySimpleValidateException
    if any of the arguments are invalid."""

    if not isinstance(blank, bool):
        raise PySimpleValidateException('blank argument must be a bool')

    if not isinstance(strip, (bool, str, type(None))):
        raise PySimpleValidateException('strip argument must be a bool, None, or str')

    if blacklist is None:
        blacklist = [] # blacklist defaults to a blank list.

    try:
        len(blacklist) # Make sure blacklist is a sequence.
        for response in blacklist:
            if len(response) != 2:
                raise Exception() # Run the code in the except clause.
            if not isinstance(response[0], str) or not isinstance(response[1], str):
                raise Exception() # Run the code in the except clause.
    except:
        raise PySimpleValidateException('blacklist must be a sequence of (regex_str, str) tuples')


def _validateParamsFor_validateNum(min=None, max=None, lessThan=None, greaterThan=None):
    for name, val in (('min', min), ('max', max),
                      ('lessThan', lessThan), ('greaterThan', greaterThan)):
        if not isinstance(val, (int, float, type(None))):
            raise PySimpleValidateException(name + ' argument must be int, float, or NoneType')


def validateNum(value, blank=False, strip=True, blacklist=None, _numType='num',
                min=None, max=None, lessThan=None, greaterThan=None):
    """Returns None if value is a number. TODO"""
    # Validate parameters.
    value = str(value)
    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)
    _validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    if _handleBlankValues(value, blank, strip) is True:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

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

    # Get specific response.
    result = _getBlacklistResponse(value, blacklist)
    if result is not None:
        return result

    return True


def validateInt(value, blank=False, strip=True, blacklist=None,
                min=None, max=None, lessThan=None, greaterThan=None):
    return validateNum(value=value, blank=blank, strip=strip,
                       blacklist=blacklist, _numType='int', min=min, max=max,
                       lessThan=lessThan, greaterThan=greaterThan)


def validateFloat(value, blank=False, strip=True, blacklist=None,
                min=None, max=None, lessThan=None, greaterThan=None):
    return validateNum(value=value, blank=blank, strip=strip,
                       blacklist=blacklist, _numType='float', min=min, max=max,
                       lessThan=lessThan, greaterThan=greaterThan)


def _validateParamsFor_validateChoice(choices, blank=False, strip=True, blacklist=None,
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


    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)

    for choice in choices:
        if not isinstance(choice, str):
            raise PySimpleValidateException('choice %r must be a string' % (_errstr(choice)))
    if lettered and len(choices) > 26:
        raise PySimpleValidateException('lettered argument cannot be True if there are more than 26 choices')
    if numbered and lettered:
        raise PySimpleValidateException('numbered and lettered arguments cannot both be True')


def validateChoice(value, choices, blank=False, strip=True, blacklist=None,
                   numbered=False, lettered=False, caseSensitive=False):

    # Validate parameters.
    _validateParamsFor_validateChoice(choices=choices, blank=blank, strip=strip,
        blacklist=blacklist, numbered=numbered, lettered=lettered, caseSensitive=caseSensitive)

    value = str(value)
    if _handleBlankValues(value, blank, strip) is True:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    # Validate against choices.
    if value in choices:
        return True
    if numbered and value.isdecimal() and 0 < int(value) <= len(choices):
        # Numbered options begins at 1, not 0.
        return True
    if lettered and len(value) == 1 and value.isalpha() and 0 < ord(value.upper()) - 64 <= len(choices):
        # Lettered options are always case-insensitive.
        return True
    if not caseSensitive and value.upper() in [choice.upper() for choice in choices]:
        return True

    # Get specific response.
    result = _getBlacklistResponse(value, blacklist)
    if result is not None:
        return result

    raise ValidationException(_('%r is not a valid choice.') % (_errstr(value)))


def _validateParamsFor__validateToDateTimeFormat(formats, blank=False, strip=True, blacklist=None):
    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)
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


def _validateToDateTimeFormat(value, formats, blank=False, strip=True, blacklist=None):
    # Validate parameters.
    _validateParamsFor__validateToDateTimeFormat(formats, blank=blank, strip=strip, blacklist=blacklist)

    value = str(value)
    if _handleBlankValues(value, blank, strip) is True:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    # Validate against the given formats.
    for format in formats:
        try:
            time.strptime(value, format)
        except ValueError:
            continue # If this format fails to parse, move on to the next format.
        return True
    raise ValidationException(_('%r is not a valid time formatted as %s') % (value, time.strftime(formats[0])))


def validateTime(value, blank=False, strip=True, blacklist=None,
                 formats=('%H:%M:%S', '%H:%M', '%X')):
    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        if _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, blacklist=blacklist):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid time formatted as %s') % (_errstr(value), time.strftime(formats[0])))


def validateDate(value, blank=False, strip=True, blacklist=None,
                 formats=('%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d', '%y/%m/%d', '%x')):
    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        if _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, blacklist=blacklist):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid date formatted as %s') % (_errstr(value), time.strftime(formats[0])))


def validateDatetime(value, blank=False, strip=True, blacklist=None,
                     formats=('%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S',
                              '%m/%d/%Y %H:%M', '%m/%d/%y %H:%M', '%Y/%m/%d %H:%M', '%y/%m/%d %H:%M', '%x %H:%M',
                              '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S')):
    # Reuse the logic in _validateToDateTimeFormat() for this function.
    try:
        if _validateToDateTimeFormat(value, formats, blank=blank, strip=strip, blacklist=blacklist):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid date and time formatted as %s.') % (_errstr(value), time.strftime(formats[0])))


def validateFilename(value, blank=False, strip=True, blacklist=None, mustExist=False):
    # TODO - finish this.
    if value.endswith(' '):
        raise ValidationException(_('%r is not a valid filename because it ends with a space.') % (_errstr(value)))
    raise NotImplementedError()


def validateFilepath(value, blank=False, strip=True, blacklist=None, mustExist=False):
    # TODO - finish this.
    raise NotImplementedError()


def validateIpAddr(value, blank=False, strip=True, blacklist=None):
    # Reuse the logic in validateRege()
    try:
        if validateRegex(value=value, regex=IPV4_REGEX, blank=blank, strip=strip, blacklist=blacklist):
            return True
        if validateRegex(value=value, regex=IPV6_REGEX, blank=blank, strip=strip, blacklist=blacklist):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid IP address.') % (_errstr(value)))


def _validateParamsFor_validateRegex(blank=False, strip=True, blacklist=None):
    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)


def validateRegex(value, regex='', flags=0, blank=False, strip=True, blacklist=None):
    # Validate parameters.
    _validateParamsFor_validateRegex(blank=False, strip=True, blacklist=None)
    value = str(value)

    if _handleBlankValues(value, blank, strip) is True:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    if re.compile(regex, flags).search(value) is not None:
        return True
    else:
        raise ValidationException(_('%r does not match the specified pattern.') % (_errstr(value)))


def _validateParamsFor_validateLiteralRegex(blank=False, strip=True, blacklist=None):
    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)


def validateLiteralRegex(value, blank=False, strip=True, blacklist=None):
    # TODO - I'd be nice to check regexes in other languages, i.e. JS and Perl.
    _validateParamsFor_validateRegex(blank=blank, strip=strip, blacklist=blacklist)

    try:
        re.compile(value)
    except Exception as ex:
        raise ValidationException(_('%r is not a valid regular expression: %s') % (_errstr(value), ex))


def validateURL(value, blank=False, strip=True, blacklist=None):
    # Reuse the logic in validateRege()
    try:
        if validateRegex(value=value, blank=blank, strip=strip, blacklist=blacklist):
            return True
    except ValidationException:
        raise ValidationException(_('%r is not a valid URL.') % (value))


def validateYesNo(value, blank=False, strip=True, blacklist=None, yes='yes', no='no', caseSensitive=False):
    # Validate parameters.
    value = str(value)
    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)

    yes = str(yes)
    no = str(no)
    if len(yes) == 0:
        raise PySimpleValidateException('yes argument must be a non-empty string.')
    if len(no) == 0:
        raise PySimpleValidateException('no argument must be a non-empty string.')

    if _handleBlankValues(value, blank, strip) is True:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    if caseSensitive:
        if value in (yes, no, yes[0], no[0]):
            return True
    else:
        if value.upper() in (yes.upper(), no.upper(), yes[0].upper(), no[0].upper()):
            return True

    raise ValidationException(_('%r is not a valid %s/%s response.') % (_errstr(value), yes, no))



def validateName():
    raise NotImplementedError()


def validateAddress():
    raise NotImplementedError()


def validateState(value, blank=False, strip=True, blacklist=None, caseSensitive=False):
    # Validate parameters.
    value = str(value)
    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)

    if _handleBlankValues(value, blank, strip) is True:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

    if caseSensitive:
        if value in STATES:
            return True
    else:
        if value.upper() in STATES_UPPER:
            return True

    raise ValidationException(_('%r is not a state.') % (_errstr(value)))



def validateZip(value, blank=False, strip=True, blacklist=None):
    # Validate parameters.
    value = str(value)
    _validateGenericParameters(blank=blank, strip=strip, blacklist=blacklist)

    if _handleBlankValues(value, blank, strip) is True:
        return True

    # Optionally strip whitespace or other characters from value.
    value = _getStrippedValue(value, strip)

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


def validateMonth(value, blank=False, strip=True, blacklist=None, caseSensitive=False,
                  monthNames=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
    # TODO - accept abbreviated forms and numbered months as well.
    raise NotImplementedError()

def validateDay():
    raise NotImplementedError()

def validateDayOfMonth():
    raise NotImplementedError()

def validateYear():
    raise NotImplementedError()

