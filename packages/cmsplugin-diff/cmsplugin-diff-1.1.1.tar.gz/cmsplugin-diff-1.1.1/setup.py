#!/usr/bin/env python
#
# Copyright (C) 2017 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
# pylint: disable=bad-whitespace

import os

from distutils.cmd import Command
from setuptools import setup

from cmsplugin_diff import __version__, __pkgname__

# Grab description for Pypi
with open('README.md') as fhl:
    DESC = fhl.read()

class DemoCommand(Command):
    """Run a demonstration website"""
    description = "Run the demonstration website."
    user_options = []

    def initialize_options(self):
        return []

    def finalize_options(self):
        return []

    def run(self):
        try:
            import pkg_resources
        except ImportError:
            self.warn("Can not find virtualenv, the demo needs it.")
            raise
        print("FOUND: {}".format(pkg_resources))
        os.chdir(os.path.dirname(__file__))
        if not os.path.isdir('demoenv'):
            os.system('virtualenv demoenv')
            os.system('./demoenv/bin/pip install .')
            os.system('./demoenv/bin/pip install djangocms_text_ckeditor')

        if not os.path.isfile('demo/data/demo-%s.db' % __version__):
            os.system('./demoenv/bin/python demo/manage.py migrate')
            os.system('./demoenv/bin/python demo/manage.py loaddata demodata')

        print("""

Welcome to the demo site for %s (%s). The service is running at:

    http://localhost:8841/en-gb/

        """ % (__pkgname__, __version__))
        os.system('./demoenv/bin/python demo/manage.py runserver localhost:8841')


setup(
    name             = __pkgname__,
    version          = __version__,
    description      = "Extend django-cms with history and diff views.",
    long_description = DESC,
    author           = 'Martin Owens',
    url              = 'https://github.com/doctormo/django-cmsplugin-diff',
    author_email     = 'doctormo@gmail.com',
    platforms        = 'linux',
    license          = 'AGPLv3',
    packages         = ['cmsplugin_diff'],
    install_requires = ['django-cms>=3.5', 'diff_match_patch>=20121119'],
    classifiers      = [
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass={
        'demo': DemoCommand,
    },
)
