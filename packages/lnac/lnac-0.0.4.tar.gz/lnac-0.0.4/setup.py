""" LnaC installation script. """

from codecs import open
from os import path

from setuptools import find_packages, setup

import lnac

VERSION = str(lnac.__version__)
DOWNLOAD_URL = ''

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'lnac',
    version = VERSION,

    description = 'A toy functional language compiler written in Python',
    long_description = long_description,
    long_description_content_type = 'text/markdown',

    url = 'https://github.com/typicaltuesday/lna',

    author = 'Lena',
    author_email = 'typicaltuedsay@gmail.com',

    license = 'Apache License 2.0',

    keywords = 'lnac lna compiler functional programming parsing lexing',
    packages = find_packages(exclude=[ 'build', 'demos' ]),
    install_requires = [],
    package_data = {},

    entry_points = {
        'console_scripts': [
            'lnac = lnac.main:main',
        ],
    },

    download_url = DOWNLOAD_URL
)