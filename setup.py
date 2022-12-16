# Copyright 2022 Kaloian Manassiev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''Setup logic for the PyMM package'''

import os

from setuptools import setup


def read(fname):
    '''Utility function to read the README/LICENSE files.'''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='PyMM',
    version='0.0.1',
    author='Kaloian Manassiev',
    author_email='kaloianm@gmail.com',
    description=('Python module which is an object-oriented front to the ModemManager D-Bus API.'),
    long_description=read('README.md'),
    license=read('LICENSE'),
    packages=['PyMM'],
    entry_points={
        'console_scripts': ['PyMMUI=PyMMUI:application_main'],
    },
)
