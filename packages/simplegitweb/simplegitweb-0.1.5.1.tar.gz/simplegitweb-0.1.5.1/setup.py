#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'simplegitweb',
    version = '0.1.5.1',
    author = 'dengyt',
    author_email = 'dengyt@dengyt.net',
    description = ('A Python git web server that base on dulwich lib'),
    license = 'Apache License, Version 2.0',
    keywords = 'git gitserver gitweb version control',
    packages = ['simplegitweb', 'simplegitweb.templates', 'simplegitweb.systemd'],
    package_data = {
        'simplegitweb': ['templates/*.html', 'systemd/*'],
        },
    include_package_data = True,
    install_requires=[
        'dulwich>=0.19.0',
        'pathlib>=1.0.0',
        'configparser>=3.5.0',
        'Jinja2>=2.0',
        'click>=6.0'
        ],
    zip_safe = False
    )
