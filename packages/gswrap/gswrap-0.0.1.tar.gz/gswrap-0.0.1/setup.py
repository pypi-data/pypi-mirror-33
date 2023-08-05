#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

requires = [
    'google-api-python-client==1.7.3',
    'httplib2==0.11.3',
    'oauth2client==4.1.2',
    'pyasn1==0.4.3',
    'pyasn1-modules==0.2.1',
    'rsa==3.4.2',
    'six==1.11.0',
    'uritemplate==3.0.0',
]

def main():
    description = 'gswrap is wrapper libs for Google Sheet Rest API.'

    setup(
        name='gswrap',
        version='0.0.1',
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
