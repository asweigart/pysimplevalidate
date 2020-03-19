from setuptools import setup, find_packages
import os
import re

# Load version from module (without loading the whole module)
with open('src/pysimplevalidate/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()




setup(
    name='PySimpleValidate',
    version=version,
    url='https://github.com/asweigart/pysimplevalidate',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('A collection of string-based validation functions, suitable for use in other Python 2 and 3 applications.'),
    long_description=long_description,
    license='BSD',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    test_suite='tests',
    install_requires=['typing;python_version<"3.5"'],
    keywords="input validation text string",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)