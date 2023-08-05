import os
import sys

from setuptools import setup, find_packages


def get_version(flavor='version'):
    prop = flavor.upper()
    sys.path.insert(0, os.path.abspath('src'))
    import getrest

    return getattr(getrest, prop)


def readfile(filename='README.rst'):
    with open(filename, 'rb') as f:
        text = f.read()
        f.close()

    return text.decode('utf-8')


install_requires = [
    'requests>=2.18', 'urlobject>=2.4',
]

if sys.version_info.minor < 5:
    install_requires.append('typing')

setup(
    version=get_version('release'),
    long_description=readfile(),
    install_requires=install_requires,
    tests_require='nose2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    command_options={
        'build_sphinx': {
            'version': ('setup.py', get_version()),
            'release': ('setup.py', get_version('release')),
        }
    },
)
