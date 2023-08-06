#! /usr/bin/python
# =============================================================================
#
# Copyright (c)  2016, Cisco Systems
# All rights reserved.
#
# # Author: Klaudiusz Staniek
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# =============================================================================

"""
 Installation script for accelerated upgrade
"""
import codecs
import re
import sys

from setuptools.command.test import test as TestCommand

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



DESCRIPTION = 'This is a python module providing access to Cisco devices over Telnet and SSH'
with codecs.open('README.md', 'r', encoding='UTF-8') as readme:
    LONG_DESCRIPTION = ''.join(readme)

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: POSIX :: Linux',
]

packages = [
    'condoor',
    'condoor.protocols',
    'condoor.drivers',
]

NAME = 'condoor'


def version():
    pyfile = 'condoor/version.py'
    with open(pyfile) as fp:
        data = fp.read()

    match = re.search("__version__ = '([^']+)'", data)
    assert match, 'cannot find version in {}'.format(pyfile)
    return match.group(1)


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #  import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name=NAME,
    version=version(),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Klaudiusz Staniek',
    author_email='klstanie@cisco.com',
    url='https://github.com/kstaniek/condoor',
    download_url='https://github.com/kstaniek/condoor/tarball/{}'.format(version()),
    keywords='cisco,automation',
    tests_require=['tox'],
    cmdclass={'test': Tox},
    platforms=['any'],
    packages=packages,
    package_data={'': ['LICENSE', ], },
    package_dir={'condoor': 'condoor'},
    include_package_data=True,
    install_requires=['pexpect>=4.2.1', 'pyyaml'],
    data_files=[('condoor', ['condoor/patterns.yaml', 'condoor/config.yaml'])],
    license='Apache 2.0',
    classifiers=CLASSIFIERS,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'condoor = condoor.__main__:run',
        ]
    }
)
