import os
import sys

import pytest
# NOTE: PySimpleValidate tests using PyTest 3.6.3. Doesn't support versions before 3.0.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pysimplevalidate as pysv


# TODO - These tests don't cover non-English strings.

def test__errstr():
    pysv.MAX_ERROR_STR_LEN == 50 # Make sure this constant hasn't changed.

    pysv.MAX_ERROR_STR_LEN = 50 # Set it to 50 for the purposes of this test.

    assert pysv._errstr('ABC') == 'ABC'
    assert pysv._errstr('X' * 50) == 'X' * 50
    assert pysv._errstr('X' * 51) == 'X' * 50 + '...'

def test_handleBlankValues():
    assert pysv._handleBlankValues('', blank=True, strip=False) is True # Test that blank string passes.
    with pytest.raises(pysv.ValidationException, message='Blank values are not allowed.'):
        pysv._handleBlankValues('', blank=False, strip=False) # Test that blank string fails.
    with pytest.raises(pysv.ValidationException, message='Blank values are not allowed.'):
        pysv._handleBlankValues(' ', blank=False, strip=True)
    assert pysv._handleBlankValues(' ', blank=True, strip=True) is True # Test that blank string passes.
    assert pysv._handleBlankValues('X', blank=False, strip=False) is None
    assert pysv._handleBlankValues(' X ', blank=False, strip=True) is None


def test__validateGenericParameters():
    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=None) is None
    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=[], blacklistRegexes=None) is None
    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=['valid'], blacklistRegexes=None) is None

    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=None) is None
    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=[]) is None
    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=[('x', 'x')]) is None
    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=[('x', 'x'), ('x', 'x')]) is None

    assert pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=['x']) is None

    with pytest.raises(pysv.PySimpleValidateException):
        pysv._validateGenericParameters(blank=None, strip=True, whitelistRegexes=None, blacklistRegexes=[])

    with pytest.raises(pysv.PySimpleValidateException):
        pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=42)

    with pytest.raises(pysv.PySimpleValidateException):
        pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=[('x', 42)])

    with pytest.raises(pysv.PySimpleValidateException):
        pysv._validateGenericParameters(blank=True, strip=True, whitelistRegexes=None, blacklistRegexes=[(42, 'x')])





def test_validateNum():
    assert pysv.validateNum('42')
    assert pysv.validateNum('3.14')
    assert pysv.validateNum(42)  # Non-strings should be fine.
    assert pysv.validateNum(3.14)

    with pytest.raises(pysv.ValidationException, message="'ABC' is not a number."):
        pysv.validateNum('ABC')
    with pytest.raises(pysv.ValidationException, message='Blank values are not allowed.'):
        pysv.validateNum('')
    assert pysv.validateNum('', blank=True)
    assert pysv.validateNum('XXX', blank=True, strip='X')
    with pytest.raises(pysv.ValidationException, message="' ' is not a number."):
        pysv.validateNum(' ', blank=True, strip=False)

    # Duplicate, but setting _numType explicitly:
    assert pysv.validateNum('42', _numType='num')
    assert pysv.validateNum('3.14', _numType='num')
    assert pysv.validateNum(42, _numType='num')  # Non-strings should be fine.
    assert pysv.validateNum(3.14, _numType='num')

    with pytest.raises(pysv.ValidationException, message="'ABC' is not a number."):
        pysv.validateNum('ABC', _numType='num')
    with pytest.raises(pysv.ValidationException, message='Blank values are not allowed.'):
        pysv.validateNum('', _numType='num')
    assert pysv.validateNum('', blank=True, _numType='num')
    with pytest.raises(pysv.ValidationException, message="' ' is not a number."):
        pysv.validateNum(' ', blank=True, strip=False, _numType='num')

    # TODO - need to test strip, blacklistRegexes

def test_validateInt():
    assert pysv.validateInt('42')
    with pytest.raises(pysv.ValidationException, message="'3.14' is not an integer."):
        pysv.validateInt('3.14')
    assert pysv.validateInt(42)  # Non-strings should be fine.
    with pytest.raises(pysv.ValidationException, message="'3.14' is not an integer."):
        pysv.validateInt(3.14)

    with pytest.raises(pysv.ValidationException, message="'ABC' is not an integer."):
        pysv.validateInt('ABC')
    with pytest.raises(pysv.ValidationException, message='Blank values are not allowed.'):
        pysv.validateInt('')
    assert pysv.validateInt('', blank=True)
    with pytest.raises(pysv.ValidationException, message="' ' is not an integer."):
        pysv.validateInt(' ', blank=True, strip=False)


    # Call validateNum() but setting _numType explicitly:
    assert pysv.validateNum('42', _numType='int')
    with pytest.raises(pysv.ValidationException, message="'3.14' is not an integer."):
        pysv.validateNum('3.14', _numType='int')
    assert pysv.validateNum(42, _numType='int')  # Non-strings should be fine.
    with pytest.raises(pysv.ValidationException, message="'3.14' is not an integer."):
        pysv.validateNum(3.14, _numType='int')

    with pytest.raises(pysv.ValidationException, message="'ABC' is not an integer."):
        pysv.validateNum('ABC', _numType='int')
    with pytest.raises(pysv.ValidationException, message='Blank values are not allowed.'):
        pysv.validateNum('', _numType='int')
    assert pysv.validateNum('', blank=True, _numType='int')
    with pytest.raises(pysv.ValidationException, message="' ' is not an integer."):
        pysv.validateNum(' ', blank=True, strip=False, _numType='int')


def test_validateChoice():
    assert pysv.validateChoice('42', ('42', 'cat', 'dog'))
    assert pysv.validateChoice('42', ['42', 'cat', 'dog'])

    assert pysv.validateChoice('a', ['42', 'cat', 'dog'], lettered=True)
    assert pysv.validateChoice('A', ['42', 'cat', 'dog'], lettered=True)
    assert pysv.validateChoice('c', ['42', 'cat', 'dog'], lettered=True)
    assert pysv.validateChoice('C', ['42', 'cat', 'dog'], lettered=True)

    assert pysv.validateChoice('1', ['42', 'cat', 'dog'], numbered=True)
    assert pysv.validateChoice('3', ['42', 'cat', 'dog'], numbered=True)


    with pytest.raises(pysv.PySimpleValidateException):
        # Lettered and numbered can't both be True.
        pysv.validateChoice('42', ['42', 'cat', 'dog'], lettered=True, numbered=True)

    with pytest.raises(pysv.PySimpleValidateException):
        pysv.validateChoice('42', ['42'] * 27, lettered=True)

    with pytest.raises(pysv.ValidationException, message="'D' is not a valid choice."):
        pysv.validateChoice('D', ['42', 'cat', 'dog'], lettered=True)
    with pytest.raises(pysv.ValidationException, message="'4' is not a valid choice."):
        pysv.validateChoice('4', ['42', 'cat', 'dog'], numbered=True)
    with pytest.raises(pysv.ValidationException, message="'0' is not a valid choice."):
        pysv.validateChoice('0', ['42', 'cat', 'dog'], numbered=True)

    with pytest.raises(pysv.ValidationException, message="'XXX' is not a valid choice."):
        pysv.validateChoice('XXX', ['42', 'cat', 'dog'])


def test_validateDate():
    assert pysv.validateDate('2018/7/10')
    assert pysv.validateDate('18/7/10')
    assert pysv.validateDate('7/10/2018')
    assert pysv.validateDate('7/10/18')

    with pytest.raises(pysv.ValidationException): #, message="'2018/13/10' is not a valid date."):
        pysv.validateDate('2018/13/10')

    # TODO - finish


def test_validateTime():
    assert pysv.validateTime('00:00')
    assert pysv.validateTime('12:00')
    assert pysv.validateTime('7:00')
    assert pysv.validateTime('00:00:00')
    assert pysv.validateTime('12:00:00')
    assert pysv.validateTime('7:00:00')

    with pytest.raises(pysv.ValidationException): #, message="'25:00' is not a valid time."):
        pysv.validateTime('25:00')
    with pytest.raises(pysv.ValidationException): #, message="'25:0:00' is not a valid time."):
        pysv.validateTime('25:0:00')
    with pytest.raises(pysv.ValidationException): #, message="'7:61' is not a valid time."):
        pysv.validateTime('7:61')
    with pytest.raises(pysv.ValidationException): #, message="'7:61:00' is not a valid time."):
        pysv.validateTime('7:61:00')
    with pytest.raises(pysv.ValidationException): #, message="'7:30:62' is not a valid time."):
        pysv.validateTime('7:30:62')
    with pytest.raises(pysv.ValidationException): #, message="'XXX' is not a valid time."):
        pysv.validateTime('XXX')

    # TODO - finish


def test_validateDatetime():
    assert pysv.validateDatetime('2018/7/10 12:30:00')
    assert pysv.validateDatetime('2018/7/10 12:30')
    assert pysv.validateDatetime('2018/7/1 23:00')

    # TODO - finish

def test_validateURL():
    assert pysv.validateURL('https://www.metafilter.com/')
    assert pysv.validateURL('www.metafilter.com')
    assert pysv.validateURL('https://www.metafilter.com/175250/Have-you-ever-questioned-the-nature-of-your-streaming-content')

#def test_validateFilename():
#    assert pysv.validateFilename('foo.txt')


def test_validateRegex():
    assert pysv.validateRegex('cat', 'cat')
    assert pysv.validateRegex('cat', r'\w+')
    assert pysv.validateRegex('cat 123', r'\d+')


def test_validateLiteralRegex():
    assert pysv.validateRegex(r'\w+')
    assert pysv.validateRegex(r'(')


def test_validateIpAddr():
    assert pysv.validateIpAddr('127.0.0.1')
    assert pysv.validateIpAddr('255.255.255.255')
    assert pysv.validateIpAddr('300.255.255.255')

def test_validateYesNo():
    assert pysv.validateYesNo('yes')
    assert pysv.validateYesNo('y')
    assert pysv.validateYesNo('no')
    assert pysv.validateYesNo('n')

    assert pysv.validateYesNo('YES')
    assert pysv.validateYesNo('Y')
    assert pysv.validateYesNo('NO')
    assert pysv.validateYesNo('N')

    assert pysv.validateYesNo('si', yes='si')
    assert pysv.validateYesNo('SI', yes='si')
    assert pysv.validateYesNo('n', yes='oui', no='no')


def test_validateState():
    assert pysv.validateState('CA')
    assert pysv.validateState('California')


def test_validateZip():
    assert pysv.validateZip('94105')
    with pytest.raises(pysv.ValidationException, message="'XXX' is not a zip code."):
        pysv.validateZip('XXX')


def test__validateParamsFor_validateChoice():
    # Note that these calls raise PySimpleValidateException, not
    # ValidationException, because they are problems with the call itself,
    # not with the value being validated.

    pysv._validateParamsFor_validateChoice(['dog', 'cat']) # Make sure no exceptions are raised.

    with pytest.raises(pysv.PySimpleValidateException, message='choices arg must be a sequence'):
        pysv._validateParamsFor_validateChoice(42)

    with pytest.raises(pysv.PySimpleValidateException, message='choices must have at least two items if blank is False'):
        pysv._validateParamsFor_validateChoice([])

    with pytest.raises(pysv.PySimpleValidateException, message='choices must have at least one item'):
        pysv._validateParamsFor_validateChoice([], blank=True)

    with pytest.raises(pysv.PySimpleValidateException, message='choices must have at least one item'):
        pysv._validateParamsFor_validateChoice([], blank=True)

    with pytest.raises(pysv.PySimpleValidateException, message='caseSensitive argument must be a bool'):
        pysv._validateParamsFor_validateChoice(['dog', 'cat'], caseSensitive=None)

def test__validateParamsFor_validateNum():
    pysv._validateParamsFor_validateNum() # Make sure no exceptions are raised.

    with pytest.raises(pysv.PySimpleValidateException, message=' min argument must be int, float, or NoneType'):
        pysv._validateParamsFor_validateNum(min='invalid')

    with pytest.raises(pysv.PySimpleValidateException, message=' max argument must be int, float, or NoneType'):
        pysv._validateParamsFor_validateNum(max='invalid')

    with pytest.raises(pysv.PySimpleValidateException, message=' lessThan argument must be int, float, or NoneType'):
        pysv._validateParamsFor_validateNum(lessThan='invalid')

    with pytest.raises(pysv.PySimpleValidateException, message=' greaterThan argument must be int, float, or NoneType'):
        pysv._validateParamsFor_validateNum(greaterThan='invalid')

if __name__ == '__main__':
    pytest.main()


