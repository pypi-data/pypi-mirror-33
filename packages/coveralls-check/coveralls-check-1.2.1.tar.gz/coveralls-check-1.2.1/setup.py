# See LICENSE.rst for license details.
# Copyright (c) 2017-2018 Chris Withers

import os

from setuptools import setup, find_packages

setup(
    name='coveralls-check',
    version='1.2.1',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description="Check coverage at https://coveralls.io",
    long_description=open('README.rst').read(),
    url='https://github.com/cjw296/coverage-check',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    py_modules=['coveralls_check'],
    zip_safe=False,
    include_package_data=True,
    install_requires=['requests', 'backoff'],
    extras_require=dict(
        test=['pytest', 'testfixtures', 'responses', 'coveralls', 'mock'],
        build=['setuptools-git', 'twine', 'wheel']
    ),
    entry_points={
        'console_scripts': [
            'coveralls-check = coveralls_check:main',
        ]
    },
)
