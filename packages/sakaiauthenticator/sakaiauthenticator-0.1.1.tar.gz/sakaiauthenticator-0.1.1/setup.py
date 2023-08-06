###########################################################################
# sakaiauthenticator is Copyright (C) 2018 Kyle Robbertze
# <krobbertze@gmail.com>
#
# Top30 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# sakaiauthenticator is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sakaiauthenticator. If not, see
# <http://www.gnu.org/licenses/>.
###########################################################################
"""
sakaiauthenticator is a Python 3 module that allows Django authentication to
occur using Sakai
"""
from codecs import open
from setuptools import setup, find_packages

setup(
    name='sakaiauthenticator',
    version='0.1.1',
    description='Allows Django authentication using Sakai',
    long_description='sakaiauthenticator is a Django backend that allows authentication to occur using Sakai, the open source learning platform',
    url='https://gitlab.com/bubbles/sakaiauthenticator',
    author='Kyle Robbertze',
    author_email='krobbertze@gmail.com',
    license='GPL-3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Software Development',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='django sakai authentication backend',
    packages=find_packages(),
    install_requires=['django', 'SakaiPy'],
    package_data={
        '': ['LICENCE.md'],
    },
)
