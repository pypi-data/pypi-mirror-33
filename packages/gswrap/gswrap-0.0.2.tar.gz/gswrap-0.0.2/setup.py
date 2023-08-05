#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

requires = [
    'google-api-python-client',
    'httplib2',
    'oauth2client',
    'pyasn1',
    'pyasn1-modules',
    'rsa',
    'six',
    'uritemplate',
]

def main():
    description = 'gswrap is wrapper libs for Google Sheet Rest API.'

    setup(
        name='gswrap',
        version='0.0.2',
        author='nabeen',
        author_email='watanabe_kenichiro@hasigo.co.jp',
        url='https://github.com/nabeen/gswrap',
        description=description,
        long_description=description,
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(),
        install_requires=requires,
        tests_require=[],
        setup_requires=[],
    )


if __name__ == '__main__':
    main()
