# Copyright (c) 2018 WeFindX Foundation, CLG.
# All Rights Reserved.

from setuptools import find_packages, setup

setup(
    name='typology',
    version='0.0.9',
    description='Python formats derived from vocabulary concepts.',
    url='https://gitlab.com/wefindx/typology',
    author='Mindey',
    author_email='mindey@qq.com',
    license='ASK FOR PERMISSIONS',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=['metawiki', 'requests', 'bs4', 'mistune', 'PyYAML'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
