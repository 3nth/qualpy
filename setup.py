#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import qualpy

config = {
    'description': 'your qualtrics buddy',
    'author': 'Derek Flenniken',
    'url': 'https://github.com/3nth/qualpy',
    'download_url': 'https://github.com/3nth/qualpy',
    'author_email': 'derek.flenniken@ucsf.edu',
    'version': qualpy.__version__,
    'install_requires': ['nose', 'BeautifulSoup4', 'lxml', 'requests', 'cliff'],
    'packages': ['qualpy'],
    'package_dir': {'qualpy': 'qualpy'},
    'package_data': {'qualpy': ['*.html']},
    'scripts': [],
    'entry_points': {
        'console_scripts': [
            'qualpy = qualpy.main:main'
        ],
        'qualpy': [
            'list = qualpy.main:List',
            'document = qualpy.document:Document',
            'download = qualpy.download:Download'
        ],
    },
    'name': 'qualpy',
    'zip_safe': False,
}

setup(**config)