#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import io


NAME = 'simplegitweb'
VERSION = None
AUTHOR = 'dengyt'
AUTHOR_EMAIL = 'dengyt@dengyt.net'
DESCRIPTION = ('A Python git web server that base on dulwich lib')
REQUIRED = [
    'dulwich>=0.19.0',
    'pathlib>=1.0.0',
    'configparser>=3.5.0',
    'Jinja2>=2.0',
    'click>=6.0'
]
KEYWORDS = 'git gitserver gitweb version control'
URL = 'https://pypi.org/project/simplegitweb/'

here = os.path.abspath(os.path.dirname(__file__))

about = dict()
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION
    
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name = NAME,
    version = about['__version__'],
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license = 'Apache License, Version 2.0',
    keywords = KEYWORDS,
    url = URL,
    packages = find_packages(),
    include_package_data = True,
    install_requires = REQUIRED,
    zip_safe = False,
    classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Operating System :: POSIX',
          'Topic :: Software Development :: Version Control',
      ]
)
