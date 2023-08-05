#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Horacio G. de Oro",
    author_email='hgdeoro@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Network lock based on TCP sockets",
    entry_points={
        'console_scripts': [
            'tcpnetlock_server=tcpnetlock.cli.server:main',
            'tcpnetlock_client=tcpnetlock.cli.client:main',
            'run_with_lock=tcpnetlock.cli.run_with_lock:main'
        ],
    },
    scripts=['bin/tcpnetlock-functions.sh'],
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='tcpnetlock',
    name='tcpnetlock',
    packages=find_packages(include=['tcpnetlock', 'tcpnetlock.cli']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/hgdeoro/tcpnetlock',
    version='0.0.7',
    zip_safe=False,
)
