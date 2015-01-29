#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import qualpy

config = {
    'name': 'qualpy',
    'description': 'your qualtrics buddy',
    'version': qualpy.__version__,
    'url': 'https://github.com/3nth/qualpy',
    'license': 'MIT License',
    'author': 'Derek Flenniken',
    'download_url': 'https://github.com/3nth/qualpy',
    'author_email': 'derek.flenniken@ucsf.edu',
    'tests_require': ['nose'],
    'install_requires': ['BeautifulSoup4', 'lxml', 'requests', 'cliff', 'Jinja2'],
    'packages': ['qualpy'],
    'package_dir': {'qualpy': 'qualpy'},
    'package_data': {'qualpy': ['*.html']},
    'platform': 'any',
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
    
    'zip_safe': False,
    'classifiers': [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
}

setup(**config)