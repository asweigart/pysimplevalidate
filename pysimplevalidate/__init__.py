# PySimpleValidate
# By Al Sweigart

# TODO: Add "strict mode"
from __future__ import absolute_import, division, print_function

import re
import time




__version__ = '0.1.0'


CACHE_REGEXES_ENABLED = True
MAX_ERROR_STR_LEN = 50


REGEX_CACHE = {}

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


def _getResponse(value, responses):
	"""Where responses is a list of ('regex', 'response') tuples, this function
	returns the first response string whose regex matches value. Returns None
	if the value matches none of the responses."""

	# NOTE: responses is not validated in this private function.

	if responses is None:
		return

	for regex, response in responses:
		if CACHE_REGEXES_ENABLED:
			if regex not in REGEX_CACHE:
				# Add the regex to the regex cache.
				REGEX_CACHE[regex] = re.compile(regex)
			regexObj = REGEX_CACHE[regex] # Use the regex from the regex cache.
		else:
			# Compile the regex here and now.
			regexObj = re.compile(regex)

		mo = regexObj.search(value)
		if mo is not None:
			# Return the response that matches this regex.
			return response


def _validateGenericParameters(blank, strip, responses):
	"""Returns None if the blank, strip, and responses parameters that all
	of PySimpleValidate's validation functions have. Raises a PySimpleValidateException
	if any of the arguments are invalid."""
	if not isinstance(blank, bool):
		raise PySimpleValidateException('blank argument must be a bool')
	if not isinstance(strip, (bool, str)):
		raise PySimpleValidateException('strip argument must be a bool or str')

	if responses is None:
		responses = [] # responses defaults to a blank list.

	try:
		len(responses) # Make sure responses is a sequence.
		for response in responses:
			if len(response) != 2:
				raise Exception() # Run the code in the except clause.
			if not isinstance(response[0], str) or not isinstance(response[1], str):
				raise Exception() # Run the code in the except clause.
	except:
		raise PySimpleValidateException('responses must be a sequence of (regex_str, str) tuples')


def validateNum(value, blank=False, strip=True, responses=None, _numType='num',
				min=None, max=None, lessThan=None, greaterThan=None):
	"""Returns None if value is a number. TODO"""
	# Validate parameters.
	value = str(value)
	_validateGenericParameters(blank=blank, strip=strip, responses=responses)

	for name, val in (('min', min), ('max', max),
					  ('lessThan', lessThan), ('greaterThan', greaterThan)):
		if not isinstance(val, (int, float, type(None))):
			raise PySimpleValidateException(name + ' argument must be int, float, or NoneType')


	if _handleBlankValues(value, blank, strip) is True:
		return True

	# Optionally strip whitespace or other characters from value.
	value = _getStrippedValue(value, strip)

	# Validate the value's type (and convert value back to a number type).
	if _numType == 'num':
		try:
			value = float(value)
		except:
			raise ValidationException(_('%r is not a number.') % (_errstr(value)))
	elif _numType == 'int':
		try:
			value = int(value)
		except:
			raise ValidationException(_('%r is not an integer.') % (_errstr(value)))

	# Validate against min argument.
	if min is not None and value < min:
		raise ValidationException(_('%s must be at minimum %s.') % (_errstr(value), min))

	# Validate against max argument.
	if max is not None and value > max:
		raise ValidationException(_('%s must be at maximum %s.') % (_errstr(value), max))

	# Validate against max argument.
	if lessThan is not None and value >= lessThan:
		raise ValidationException(_('%s must be less than %s.') % (_errstr(value), lessThan))

	# Validate against max argument.
	if greaterThan is not None and value <= greaterThan:
		raise ValidationException(_('%s must be greater than %s.') % (_errstr(value), greaterThan))

	# Get specific response.
	result = _getResponse(value, responses)
	if result is not None:
		return result

	return True


def validateInt(value, blank=False, strip=True, responses=None,
				min=None, max=None, lessThan=None, greaterThan=None):
	return validateNum(value=value, blank=blank, strip=strip,
					   responses=responses, _numType='int', min=min, max=max,
					   lessThan=lessThan, greaterThan=greaterThan)


def validateChoice(value, choices=[], blank=False, strip=True, responses=None,
				   numbered=False, lettered=False, caseSensitive=False):
	# Validate parameters.
	#import pdb;pdb.set_trace()
	value = str(value)
	_validateGenericParameters(blank=blank, strip=strip, responses=responses)
	if not isinstance(caseSensitive, bool):
		raise PySimpleValidateException('caseSensitive argument must be a bool')


	if len(choices) == 0:
		raise PySimpleValidateException('choices must have at least one item')
	for choice in choices:
		if not isinstance(choice, str):
			raise PySimpleValidateException('choice %r must be a string' % (_errstr(choice)))
	if lettered and len(choices) > 26:
		raise PySimpleValidateException('lettered argument cannot be True if there are more than 26 choices')
	if numbered and lettered:
		raise PySimpleValidateException('numbered and lettered arguments cannot both be True')

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
	result = _getResponse(value, responses)
	if result is not None:
		return result

	raise ValidationException(_('%r is not a valid choice.') % (_errstr(value)))


def validateDate(value, blank=False, strip=True, responses=None,
				 formats=('%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d', '%y/%m/%d', '%x')):
	# Reuse the logic in validateDate() for this function.
	try:
		if validateTime(value, blank=blank, strip=strip, responses=responses, formats=formats):
			return True
	except ValidationException:
		raise ValidationException(_('%r is not a valid date.') % (_errstr(value)))


def validateDatetime(value, blank=False, strip=True, responses=None,
					 formats=('%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S',
						  	  '%m/%d/%Y %H:%M', '%m/%d/%y %H:%M', '%Y/%m/%d %H:%M', '%y/%m/%d %H:%M', '%x %H:%M',
							  '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S')):
	# Reuse the logic in validateDate() for this function.
	try:
		if validateTime(value, blank=blank, strip=strip, responses=responses, formats=formats):
			return True
	except ValidationException:
		raise ValidationException(_('%r is not a valid date.') % (_errstr(value)))


def validateFilename(value, blank=False, strip=True, responses=None, exists=False):

	if value.endswith(' '):
		raise ValidationException(_('%r is not a valid filename because it ends with a space.') % (_errstr(value)))
	raise NotImplementedError()


def validateFilepath(value, blank=False, strip=True, responses=None, ):
	raise NotImplementedError()


def validateIpAddr(value, blank=False, strip=True, responses=None, ):
	# Reuse the logic in validateRege()
	try:
		if validateRegex(value=value, regex=IPV4_REGEX, blank=blank, strip=strip, responses=responses):
			return True
		if validateRegex(value=value, regex=IPV6_REGEX, blank=blank, strip=strip, responses=responses):
			return True
	except ValidationException:
		raise ValidationException(_('%r is not a valid IP address.') % (_errstr(value)))


def validateRegex(value, regex='', flags=0, blank=False, strip=True, responses=None, cacheRegex=False):
	# Validate parameters.
	value = str(value)
	_validateGenericParameters(blank=blank, strip=strip, responses=responses)

	if _handleBlankValues(value, blank, strip) is True:
		return True

	# Optionally strip whitespace or other characters from value.
	value = _getStrippedValue(value, strip)

	if regex in REGEX_CACHE:
		regexObj = REGEX_CACHE[regex]
	else:
		# Compile the regex object.
		regexObj  = re.compile(regex, flags)

		if cacheRegex or CACHE_REGEXES_ENABLED:
			REGEX_CACHE[regex] = regexObj

	if regexObj.search(value) is not None:
		return True
	else:
		raise ValidationException(_('%r does not match the specified pattern.') % (_errstr(value)))



def validateLiteralRegex(value, blank=False, strip=True, responses=None):
	# TODO - I'd be nice to check regexes in other languages, i.e. JS and Perl.
	try:
		re.compile(value)
	except Exception as ex:
		raise ValidationException(_('%r is not a valid regular expression: %s') % (_errstr(value), ex))


def validateTime(value, blank=False, strip=True, responses=None,
				 formats=('%H:%M:%S', '%H:%M', '%X')):
	# Validate parameters.
	value = str(value)
	_validateGenericParameters(blank=blank, strip=strip, responses=responses)

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
	raise ValidationException(_('%r is not a valid time.') % value)



def validateURL(value, blank=False, strip=True, responses=None):
	# Reuse the logic in validateRege()
	try:
		if validateRegex(value=value, blank=blank, strip=strip, responses=responses):
			return True
	except ValidationException:
		raise ValidationException(_('%r is not a valid URL.') % (value))


def validateYesNo(value, blank=False, strip=True, responses=None, yes='yes', no='no', caseSensitive=False):
	# Validate parameters.
	value = str(value)
	_validateGenericParameters(blank=blank, strip=strip, responses=responses)
	if not isinstance(caseSensitive, bool):
		raise PySimpleValidateException('caseSensitive argument must be a bool')

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


def validateState(value, blank=False, strip=True, responses=None, caseSensitive=False):
	# Validate parameters.
	value = str(value)
	_validateGenericParameters(blank=blank, strip=strip, responses=responses)
	if not isinstance(caseSensitive, bool):
		raise PySimpleValidateException('caseSensitive argument must be a bool')

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



def validateZip(value, blank=False, strip=True, responses=None):
	# Validate parameters.
	value = str(value)
	_validateGenericParameters(blank=blank, strip=strip, responses=responses)

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

