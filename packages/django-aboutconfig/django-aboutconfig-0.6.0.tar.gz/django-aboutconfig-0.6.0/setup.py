# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

from aboutconfig import __version__

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_STRING = '.'.join(str(s) for s in __version__)

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    with open(os.path.join(BASE_DIR, 'README.md')) as fp:
        long_description = fp.read()

setup(
    name='django-aboutconfig',
    version=VERSION_STRING,
    url='https://bitbucket.org/impala/django-aboutconfig',
    license='GPLv3+',
    description='A firefox-like about:config implementation for one-off settings in Django apps.',
    long_description=long_description,
    keywords=['django', 'library', 'configuration'],
    author='Kirill Stepanov',
    author_email='mail@kirillstepanov.me',
    packages=find_packages(),
    download_url='https://bitbucket.org/impala/django-aboutconfig/get/%s.tar.gz' % VERSION_STRING,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'Django>=1.11',
    ],
    include_package_data=True,
    zip_safe=False,
)
