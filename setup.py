try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'qualpy',
    'author': 'Derek Flenniken',
    'url': 'https://github.com/3nth/qualpy',
    'download_url': 'https://github.com/3nth/qualpy',
    'author_email': 'derek.flenniken@ucsf.edu',
    'version': '0.1',
    'install_requires': ['nose', 'json'],
    'packages': ['qualpy'],
    'scripts': ['qualpy/qualpy.py'],
    'name': 'qualpy'
}

setup(**config)