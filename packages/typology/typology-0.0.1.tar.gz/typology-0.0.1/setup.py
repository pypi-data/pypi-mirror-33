from setuptools import find_packages, setup

setup(
    name='typology',
    version='0.0.1',
    description='Python formats derived from vocabulary concepts.',
    url='https://github.com/mindey/typology',
    author='Mindey',
    author_email='mindey@qq.com',
    license='AGPL',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=[],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
