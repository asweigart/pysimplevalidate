import os
import sys

import pytest
# NOTE: PySimpleValidate tests using PyTest 3.6.3. Doesn't support versions before 3.0.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pysimplevalidate


# TODO - These tests don't cover non-English strings.

def test__errstr():
    pysimplevalidate.MAX_ERROR_STR_LEN == 50 # Make sure this constant hasn't changed.

    pysimplevalidate.MAX_ERROR_STR_LEN = 50 # Set it to 50 for the purposes of this test.

    assert pysimplevalidate._errstr('ABC') == 'ABC'
    assert pysimplevalidate._errstr('X' * 50) == 'X' * 50
    assert pysimplevalidate._errstr('X' * 51) == 'X' * 50 + '...'

def test_handleBlankValues():
    assert pysimplevalidate._handleBlankValues('', blank=True, strip=False) is True # Test that blank string passes.
    with pytest.raises(pysimplevalidate.ValidationException, message='Blank values are not allowed.'):
        pysimplevalidate._handleBlankValues('', blank=False, strip=False) # Test that blank string fails.
    with pytest.raises(pysimplevalidate.ValidationException, message='Blank values are not allowed.'):
        pysimplevalidate._handleBlankValues(' ', blank=False, strip=True)
    assert pysimplevalidate._handleBlankValues(' ', blank=True, strip=True) is True # Test that blank string passes.
    assert pysimplevalidate._handleBlankValues('X', blank=False, strip=False) is None
    assert pysimplevalidate._handleBlankValues(' X ', blank=False, strip=True) is None

def test_getResponse():
    pysimplevalidate.CACHE_REGEXES_ENABLED = False
    assert pysimplevalidate._getResponse('cat', None) is None
    assert pysimplevalidate._getResponse('cat', []) is None
    assert pysimplevalidate._getResponse('cat', [('cat', 'response1')]) == 'response1'
    assert pysimplevalidate._getResponse('cat', [('cat', 'response1'), ('cat', 'response2')]) == 'response1'
    assert pysimplevalidate._getResponse('cat', [(r'\w+', 'response1')]) == 'response1'

    # Cache the regex.
    pysimplevalidate.REGEX_CACHE == {}
    pysimplevalidate.CACHE_REGEXES_ENABLED = True
    assert pysimplevalidate._getResponse('cat', [(r'\w+', 'response1')]) == 'response1'
    assert pysimplevalidate.REGEX_CACHE != {}
    assert pysimplevalidate._getResponse('cat', [(r'\w+', 'response1')]) == 'response1'


def test__validateGenericParameters():
    assert pysimplevalidate._validateGenericParameters(blank=True, strip=True, responses=None) is None
    assert pysimplevalidate._validateGenericParameters(blank=True, strip=True, responses=[]) is None
    assert pysimplevalidate._validateGenericParameters(blank=True, strip=True, responses=[('x', 'x')]) is None
    assert pysimplevalidate._validateGenericParameters(blank=True, strip=True, responses=[('x', 'x'), ('x', 'x')]) is None

    with pytest.raises(pysimplevalidate.PySimpleValidateException):
        pysimplevalidate._validateGenericParameters(blank=None, strip=True, responses=[])

    with pytest.raises(pysimplevalidate.PySimpleValidateException):
        pysimplevalidate._validateGenericParameters(blank=True, strip=None, responses=[])

    with pytest.raises(pysimplevalidate.PySimpleValidateException):
        pysimplevalidate._validateGenericParameters(blank=True, strip=True, responses='x')

    with pytest.raises(pysimplevalidate.PySimpleValidateException):
        pysimplevalidate._validateGenericParameters(blank=True, strip=True, responses=[('x', 42)])

    with pytest.raises(pysimplevalidate.PySimpleValidateException):
        pysimplevalidate._validateGenericParameters(blank=True, strip=True, responses=[(42, 'x')])


def test_validateNum():
    assert pysimplevalidate.validateNum('42')
    assert pysimplevalidate.validateNum('3.14')
    assert pysimplevalidate.validateNum(42)  # Non-strings should be fine.
    assert pysimplevalidate.validateNum(3.14)

    with pytest.raises(pysimplevalidate.ValidationException, message="'ABC' is not a number."):
        pysimplevalidate.validateNum('ABC')
    with pytest.raises(pysimplevalidate.ValidationException, message='Blank values are not allowed.'):
        pysimplevalidate.validateNum('')
    assert pysimplevalidate.validateNum('', blank=True)
    assert pysimplevalidate.validateNum('XXX', blank=True, strip='X')
    with pytest.raises(pysimplevalidate.ValidationException, message="' ' is not a number."):
        pysimplevalidate.validateNum(' ', blank=True, strip=False)

    # Duplicate, but setting _numType explicitly:
    assert pysimplevalidate.validateNum('42', _numType='num')
    assert pysimplevalidate.validateNum('3.14', _numType='num')
    assert pysimplevalidate.validateNum(42, _numType='num')  # Non-strings should be fine.
    assert pysimplevalidate.validateNum(3.14, _numType='num')

    with pytest.raises(pysimplevalidate.ValidationException, message="'ABC' is not a number."):
        pysimplevalidate.validateNum('ABC', _numType='num')
    with pytest.raises(pysimplevalidate.ValidationException, message='Blank values are not allowed.'):
        pysimplevalidate.validateNum('', _numType='num')
    assert pysimplevalidate.validateNum('', blank=True, _numType='num')
    with pytest.raises(pysimplevalidate.ValidationException, message="' ' is not a number."):
        pysimplevalidate.validateNum(' ', blank=True, strip=False, _numType='num')

    # TODO - need to test strip, responses

def test_validateInt():
    assert pysimplevalidate.validateInt('42')
    with pytest.raises(pysimplevalidate.ValidationException, message="'3.14' is not an integer."):
        pysimplevalidate.validateInt('3.14')
    assert pysimplevalidate.validateInt(42)  # Non-strings should be fine.
    with pytest.raises(pysimplevalidate.ValidationException, message="'3.14' is not an integer."):
        pysimplevalidate.validateInt(3.14)

    with pytest.raises(pysimplevalidate.ValidationException, message="'ABC' is not an integer."):
        pysimplevalidate.validateInt('ABC')
    with pytest.raises(pysimplevalidate.ValidationException, message='Blank values are not allowed.'):
        pysimplevalidate.validateInt('')
    assert pysimplevalidate.validateInt('', blank=True)
    with pytest.raises(pysimplevalidate.ValidationException, message="' ' is not an integer."):
        pysimplevalidate.validateInt(' ', blank=True, strip=False)


    # Call validateNum() but setting _numType explicitly:
    assert pysimplevalidate.validateNum('42', _numType='int')
    with pytest.raises(pysimplevalidate.ValidationException, message="'3.14' is not an integer."):
        pysimplevalidate.validateNum('3.14', _numType='int')
    assert pysimplevalidate.validateNum(42, _numType='int')  # Non-strings should be fine.
    with pytest.raises(pysimplevalidate.ValidationException, message="'3.14' is not an integer."):
        pysimplevalidate.validateNum(3.14, _numType='int')

    with pytest.raises(pysimplevalidate.ValidationException, message="'ABC' is not an integer."):
        pysimplevalidate.validateNum('ABC', _numType='int')
    with pytest.raises(pysimplevalidate.ValidationException, message='Blank values are not allowed.'):
        pysimplevalidate.validateNum('', _numType='int')
    assert pysimplevalidate.validateNum('', blank=True, _numType='int')
    with pytest.raises(pysimplevalidate.ValidationException, message="' ' is not an integer."):
        pysimplevalidate.validateNum(' ', blank=True, strip=False, _numType='int')


def test_validateChoice():
    assert pysimplevalidate.validateChoice('42', ('42', 'cat', 'dog'))
    assert pysimplevalidate.validateChoice('42', ['42', 'cat', 'dog'])

    assert pysimplevalidate.validateChoice('a', ['42', 'cat', 'dog'], lettered=True)
    assert pysimplevalidate.validateChoice('A', ['42', 'cat', 'dog'], lettered=True)
    assert pysimplevalidate.validateChoice('c', ['42', 'cat', 'dog'], lettered=True)
    assert pysimplevalidate.validateChoice('C', ['42', 'cat', 'dog'], lettered=True)

    assert pysimplevalidate.validateChoice('1', ['42', 'cat', 'dog'], numbered=True)
    assert pysimplevalidate.validateChoice('3', ['42', 'cat', 'dog'], numbered=True)


    with pytest.raises(pysimplevalidate.PySimpleValidateException):
        pysimplevalidate.validateChoice('42', ['42', 'cat', 'dog'], lettered=True, numbered=True)

    with pytest.raises(pysimplevalidate.PySimpleValidateException):
        pysimplevalidate.validateChoice('42', ['42'] * 27, lettered=True)

    with pytest.raises(pysimplevalidate.ValidationException, message="'D' is not a valid choice."):
        pysimplevalidate.validateChoice('D', ['42', 'cat', 'dog'], lettered=True)
    with pytest.raises(pysimplevalidate.ValidationException, message="'4' is not a valid choice."):
        pysimplevalidate.validateChoice('4', ['42', 'cat', 'dog'], numbered=True)
    with pytest.raises(pysimplevalidate.ValidationException, message="'0' is not a valid choice."):
        pysimplevalidate.validateChoice('0', ['42', 'cat', 'dog'], numbered=True)

    with pytest.raises(pysimplevalidate.ValidationException, message="'XXX' is not a valid choice."):
        pysimplevalidate.validateChoice('XXX', ['42', 'cat', 'dog'])


def test_validateDate():
    assert pysimplevalidate.validateDate('2018/7/10')
    assert pysimplevalidate.validateDate('18/7/10')
    assert pysimplevalidate.validateDate('7/10/2018')
    assert pysimplevalidate.validateDate('7/10/18')

    with pytest.raises(pysimplevalidate.ValidationException, message="'2018/13/10' is not a valid date."):
        pysimplevalidate.validateDate('2018/13/10')

    # TODO - finish


def test_validateTime():
    assert pysimplevalidate.validateTime('00:00')
    assert pysimplevalidate.validateTime('12:00')
    assert pysimplevalidate.validateTime('7:00')
    assert pysimplevalidate.validateTime('00:00:00')
    assert pysimplevalidate.validateTime('12:00:00')
    assert pysimplevalidate.validateTime('7:00:00')

    with pytest.raises(pysimplevalidate.ValidationException, message="'25:00' is not a valid time."):
        pysimplevalidate.validateTime('25:00')
    with pytest.raises(pysimplevalidate.ValidationException, message="'25:0:00' is not a valid time."):
        pysimplevalidate.validateTime('25:0:00')
    with pytest.raises(pysimplevalidate.ValidationException, message="'7:61' is not a valid time."):
        pysimplevalidate.validateTime('7:61')
    with pytest.raises(pysimplevalidate.ValidationException, message="'7:61:00' is not a valid time."):
        pysimplevalidate.validateTime('7:61:00')
    with pytest.raises(pysimplevalidate.ValidationException, message="'7:30:62' is not a valid time."):
        pysimplevalidate.validateTime('7:30:62')
    with pytest.raises(pysimplevalidate.ValidationException, message="'XXX' is not a valid time."):
        pysimplevalidate.validateTime('XXX')

    # TODO - finish


def test_validateDatetime():
    assert pysimplevalidate.validateDatetime('2018/7/10 12:30:00')
    assert pysimplevalidate.validateDatetime('2018/7/10 12:30')
    assert pysimplevalidate.validateDatetime('2018/7/1 23:00')

    # TODO - finish

def test_validateURL():
    assert pysimplevalidate.validateURL('https://www.metafilter.com/')
    assert pysimplevalidate.validateURL('www.metafilter.com')
    assert pysimplevalidate.validateURL('https://www.metafilter.com/175250/Have-you-ever-questioned-the-nature-of-your-streaming-content')

#def test_validateFilename():
#    assert pysimplevalidate.validateFilename('foo.txt')


def test_validateRegex():
    assert pysimplevalidate.validateRegex('cat', 'cat')
    assert pysimplevalidate.validateRegex('cat', r'\w+')
    assert pysimplevalidate.validateRegex('cat 123', r'\d+')


def test_validateLiteralRegex():
    assert pysimplevalidate.validateRegex(r'\w+')
    assert pysimplevalidate.validateRegex(r'(')


def test_validateIpAddr():
    assert pysimplevalidate.validateIpAddr('127.0.0.1')
    assert pysimplevalidate.validateIpAddr('255.255.255.255')
    assert pysimplevalidate.validateIpAddr('300.255.255.255')

def test_validateYesNo():
    assert pysimplevalidate.validateYesNo('yes')
    assert pysimplevalidate.validateYesNo('y')
    assert pysimplevalidate.validateYesNo('no')
    assert pysimplevalidate.validateYesNo('n')

    assert pysimplevalidate.validateYesNo('YES')
    assert pysimplevalidate.validateYesNo('Y')
    assert pysimplevalidate.validateYesNo('NO')
    assert pysimplevalidate.validateYesNo('N')

    assert pysimplevalidate.validateYesNo('si', yes='si')
    assert pysimplevalidate.validateYesNo('SI', yes='si')
    assert pysimplevalidate.validateYesNo('n', yes='oui', no='no')


def test_validateState():
    assert pysimplevalidate.validateState('CA')
    assert pysimplevalidate.validateState('California')


def test_validateZip():
    assert pysimplevalidate.validateZip('94105')
    with pytest.raises(pysimplevalidate.ValidationException, message="'XXX' is not a zip code."):
        pysimplevalidate.validateZip('XXX')


if __name__ == '__main__':
    pytest.main()


