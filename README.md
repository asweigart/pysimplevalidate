# pysimplevalidate

A collection of string-based validation functions, suitable for use in other Python 2 and 3 applications.

Pass a string to these validation functions, which raise ValidationException if validation fails. Otherwise they return a platonic value of the validated string (i.e. the `validateInt('42')` returns the int `42`).



Installation
============

    pip install pysimplevalidate

Example Usage
=============

    >>> import pysimplevalidate as pysv

    >>> pysv.validateStr('    hello    ')
    'hello'

    >>> pysv.validateStr('    hello    ', strip=None)
    '    hello    '

    >>> pysv.validateStr('xxxhelloxxx', strip='x')
    'hello'

    >>> pysv.validateStr('howdy', blacklistRegexes=['^h\w+$'])
    Traceback (most recent call last):
      ...
    pysimplevalidate.ValidationException: This response is invalid.

    >>> pysv.validateStr('howdy', whitelistRegexes=['^howdy$'], blacklistRegexes=['^h\w+$'])
    'howdy'

    >>> pysv.validateStr('')
    Traceback (most recent call last):
      ...
    pysimplevalidate.ValidationException: Blank values are not allowed.

    >>> pysv.validateStr('', blank=True)
    ''

    >>> pysv.validateNum(4)
    4

    >>> pysv.validateNum('four')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'four' is not a number.

    >>> pysv.validateNum(4, min=2, max=4)
    4

    >>> pysv.validateNum(4, greaterThan=2, lessThan=4)
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: Input must be less than 4.

    >>> pysv.validateInt(4.0)
    4

    >>> pysv.validateFloat(3)
    3.0

    >>> pysv.validateChoice('Cat', ('42', 'cat', 'dog'))
    'cat'

    >>> pysv.validateChoice('cat', ['42', 'cat', 'dog'], lettered=True, caseSensitive=True)
    'cat'

    >>> pysv.validateChoice('C', ['42', 'cat', 'dog'], lettered=True)
    'dog'

    >>> pysv.validateChoice('c', ['42', 'cat', 'dog'], lettered=True)
    'dog'

    >>> pysv.validateChoice('3', ['42', 'cat', 'dog'], numbered=True)
    'dog'

    >>> pysv.validateDate('2018/7/10')
    datetime.date(2018, 7, 10)

    >>> pysv.validateTime('12:00')
    datetime.time(12, 0)

    >>> pysv.validateDatetime('2018/7/10 12:30:00')
    datetime.datetime(2018, 7, 10, 12, 30)

    >>> pysv.validateTime('hour 12 minute 00', formats=['hour %H minute %M'])
    datetime.time(12, 0)

    >>> pysv.validateURL('https://www.metafilter.com/')
    'https://www.metafilter.com/'

    >>> pysv.validateRegex('cat', r'\w+')
    'cat'

    >>> pysv.validateYesNo('y')
    'yes'

    >>> pysv.validateYesNo('NO')
    'no'

    >>> pysv.validateBool('t')
    True

    >>> pysv.validateBool('FALSE')
    False

    >>> pysv.validateIp('127.0.0.1')
    '127.0.0.1'

    >>> pysv.validateState('CA')
    'California'

    >>> pysv.validateState('CALIFORNIA')
    'California'

    >>> pysv.validateMonth(12)
    'December'

    >>> pysv.validateMonth('DEC')
    'December'

    >>> pysv.validateMonth('December')
    'December'

    >>> pysv.validateMonth('Smarch')
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: 'Smarch' is not a month.

    >>> pysv.validateDayOfWeek('mon')
    'Monday'

    >>> pysv.validateDayOfWeek('MONDAY')
    'Monday'

    >>> pysv.validateDayOfMonth(29, 1920, 2)
    29

    >>> pysv.validateDayOfMonth(29, 1921, 2)
    Traceback (most recent call last):
        ...
    pysimplevalidate.ValidationException: '29' is not a day in the month of March 1921

Common Validaton Function Parameters
====================================

All validation functions have the following parameters:

* `blank` (bool): If `True`, blank strings will be allowed as valid user input.
* `strip` (bool, str, None): If `True`, whitespace is stripped from `value`. If a str, the characters in it are stripped from value. If `None`, nothing is stripped. Defaults to `True`.
* `whitelistRegexes` (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers. Defaults to `None`.
* `blacklistRegexes` (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation. Defaults to `None`.

Other input functions may have additional parameters.


Input Functions
===============

* `validateStr()` - Accepts a string. Use this if you want the basic strip/whitelist/blacklist/blank features.
* `validateNum()` - Accepts a numeric number. Additionally has `min` and `max` parameters for inclusive bounds and `greaterThan` and `lessThan` parameters for exclusive bounds. Returns an int or float, not a str.
* `validateInt()` - Accepts an integer number. Also has `min`/`max`/`greaterThan`/`lessThan` parameters. Returns an int, not a str.
* `validateFloat()` - Accepts a floating-point number. Also has `min`/`max`/`greaterThan`/`lessThan` parameters. Returns a float, not a str.
* `validateBool()` - Accepts a case-insensitive form of `'True'`, `'T'`, `'False'`, or `'F'` and returns a bool value.
* `validateChoice()` - Accepts one of the strings in the list of strings passed for its `choices` parameter.
* `validateDate()` - Accepts a date typed in one of the `strftime` formats passed to the `formats` parameter. (This has several common formats by default.) Returns a `datetime.date` object.
* `validateDatetime()` - Same as `validateDate()`, except it handles dates and times. (This has several common formats by default.) Returns a `datetime.datetime` object.
* `validateTime()` - Same as `validateDate()`, except it handles times. (This has several common formats by default.) Returns a `datetime.time` object.
* `validateYesNo()` - Accepts a case-insensitive form of `'Yes'`, `'Y'`, `'No'`, or `'N'` and returns `'yes'` or `'no'`.
* `validateRegex()` - Accepts a str that matches the provided regular expression.
* `validateState()` - Accepts the name or abbreviation of a United States state.
* `validateMonth()` - Accepts the name, abbreviation, or number of a month (`'Jan'`, `'January'`, `'1'`, etc.).
* `validateDayOfWeek()` - Accepts the name or abbreviation of a day of the week (`'Mon'`, `'monday'`, etc.)
* `validateDayOfMonth()` - Accepts a number of the day for a month, given the year and month.

