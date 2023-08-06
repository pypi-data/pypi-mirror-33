#
# betatest setup script
#
# Copyright (c) 2018 Beta Five Ltd
#
# SPDX-License-Identifier: Apache-2.0
#

import re
import runpy
import setuptools
import sys

# Check minimum python version
if sys.version_info < (3,6):
    print('ERROR: betatest requires Python 3.6+')
    sys.exit(1)

# Pick up the version number from the source code
__version__ = runpy.run_path('betatest/version.py')['__version__']

# Pick up the long description from our readme file
long_description = open('README.md', 'r').read()

# Use the first listed maintainer as our author
first_maintainer = open('MAINTAINERS', 'r').readline().strip()
m = re.match('(.*) <(.*)>$', first_maintainer)
author_name = m.group(1)
author_email = m.group(2)

setuptools.setup(
    name = 'betatest',
    version = __version__,
    author = author_name,
    author_email = author_email,
    description = 'Testing helpers for Python 3.6+.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://gitlab.com/b5/betatest',
    packages = setuptools.find_packages(),
    classifiers = (
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'
    ),
    python_requires = '>=3.6',
    license = 'Apache License 2.0',
    platforms = ('Any'),
    include_package_data=True,
)
