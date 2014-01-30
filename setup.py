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
    'install_requires': ['nose', 'BeautifulSoup4', 'lxml', 'requests'],
    'packages': ['qualpy'],
    'scripts': ['scripts/qualpy'],
    'name': 'qualpy'
}

setup(**config)