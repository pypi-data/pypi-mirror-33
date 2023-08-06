# -*- coding: utf-8 -*-
# pylint: disable=broad-except
"""qatestlink module can be installed and configured from here"""

from os import path
from setuptools import setup, find_packages
from sys import version_info
from qatestlink.core.utils import read_file
from qatestlink.core.utils import path_format


VERSION = '0.0.9'
CURR_PATH = "{}{}".format(path.abspath(path.dirname(__file__)), '/')
INSTALL_REQUIRES = [
    'requests',
    'pytest',
    'xmltodict',
    'dicttoxml',
]

def read(file_name=None, is_encoding=True, ignore_raises=False):
    """Read file"""
    if file_name is None:
        raise Exception("File name not provided")
    if ignore_raises:
        try:
            return read_file(is_encoding=is_encoding,
                             file_path=path_format(
                                 file_path=CURR_PATH,
                                 file_name=file_name,
                                 ignore_raises=ignore_raises))
        except Exception:
            # TODO: not silence like this,
            # must be on setup.cfg, README path
            return 'NOTFOUND'
    return read_file(is_encoding=is_encoding,
                     file_path=path_format(
                         file_path=CURR_PATH,
                         file_name=file_name,
                         ignore_raises=ignore_raises))

def get_install_requires():
    """Get a list of pypi python package dependencies
    Returns:
        list -- list of dependecy package names
    """
    if version_info <= (3, 4):
        INSTALL_REQUIRES.append('enum34')
    return INSTALL_REQUIRES


setup(
    name='qatestlink',
    version=VERSION,
    license=read("LICENSE", is_encoding=False, ignore_raises=True),
    packages=find_packages(exclude=['tests']),
    description='Main automation lib',
    long_description=read("README.rst"),
    author='Netzulo Open Source',
    author_email='netzuleando@gmail.com',
    url='https://github.com/netzulo/qatestlink',
    download_url='https://github.com/netzulo/qatestlink/tarball/v{}'.format(
        VERSION),
    keywords=[
        'testing',
        'logging',
        'functional',
        'http',
        'test',
        'testlink',
        'XMLRPC',
        'requests'
    ],
    install_requires=get_install_requires(),
    setup_requires=[
        'tox',
        'pytest-runner'
    ],
    tests_require=[
        'pytest-coverage',
        'pytest-html',
        'pytest-dependency',
        'flake8'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
