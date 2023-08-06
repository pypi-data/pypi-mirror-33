import sys

import setuptools


requires = [
]

tests_require = [
    'flake8>=3.5.0',
    'flake8-import-order>=0.17.1',
    'flake8-print>=3.1.0',
    'flake8-quotes>=1.0.0',
    'pytest>=3.6.1',
    'pytest-mock>=1.10.0',
]

extras_require = {
    'test': tests_require,
    'dev': requires + tests_require
}

setup_requires = ['pytest-runner'] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else []

setuptools.setup(
    name='binary-helpers',
    description='A developer-experience focused wrapper around pack and unpack.',
    version='0.0.1',
    author='roks0n',
    author_email='haluzan.rok@gmail.com',
    url='https://github.com/deadlock-delegate/python-binary',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    install_requires=requires,
    extras_require=extras_require,
    tests_require=tests_require,
    setup_requires=setup_requires,
)
