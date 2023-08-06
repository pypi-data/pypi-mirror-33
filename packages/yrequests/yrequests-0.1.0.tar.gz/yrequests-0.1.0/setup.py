# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import sys
from codecs import open
from os import path
from setuptools import setup

author_name = 'Yoshio Iwamoto'
author_email = 'yoshiodeveloper@gmail.com'
github_user = 'yoshiodeveloper'
package_name = 'yrequests'
version = '0.1.0'
description = 'A very simple module for HTTP/1.1 requests.'
package_dir = package_name
project_url = 'https://github.com/%s/%s' % (github_user, package_name)
source_url = project_url
bug_report_url = '%s/issues' % project_url

classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
] + ['Programming Language :: Python :: %s' % v
        for v in ('2.6', '2.7', '3', '3.0', '3.1', '3.2', '3.4', '3.5', '3.6', '3.7')]

install_requires = [
    'future; python_version < "3"',
    'requests'
]

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=package_name,
    version=version,
    author=author_name,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=project_url,
    packages=['yrequests'],
    package_dir={package_name: package_dir},
    install_requires=install_requires,
    classifiers=classifiers,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    project_urls={
        'Bug Reports': bug_report_url,
        'Source': source_url,
    }
)
