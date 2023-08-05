#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import sys
from setuptools import setup, find_packages
from distutils.version import LooseVersion


def check_if_binding_existed():
    bindings = ['PyQt5', 'PySide2', 'PyQt4', 'PySide']

    for binding in bindings:
        if binding in sys.modules:
            return True

    return False


with open('README.rst') as readme_file, open('HISTORY.rst') as history_file:
    long_description = (readme_file.read() + "\n\n" + history_file.read())

"""Install Qt packages for python with specific version """

install_requires = [
    # TODO: put package requirements here
]

if check_if_binding_existed():
    print("Qt binding existed.")
else:
    is_64bits = sys.maxsize > 2**32

    python_version = "%s.%s.%s" % (
        sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    python_version = LooseVersion(python_version)

    if python_version >= LooseVersion('3.7'):
        install_requires.append('PyQt5')
    elif python_version >= LooseVersion('3.5'):
        # Released PySide2 5.11 support python3.5~ x86/x64 with Windows, MacOSX,
        # Linux
        os.system(
            ('%s -m pip install '
             '--index-url=https://download.qt.io/official_releases/QtForPython/ '
             'pyside2 --trusted-host download.qt.io') % sys.executable)

    elif python_version == LooseVersion('2.7'):
        if is_64bits:
            if sys.platform.startswith('linux'):
                # PySide support python2.7 x64 with Linux
                # References: https://stackoverflow.com/questions/24489588/how-can-i-install-pyside-on-travis
                os.system(
                    ('%s -m pip install PySide --no-index --find-links '
                     'https://parkin.github.io/python-wheelhouse/') % sys.executable)
            else:
                # Install prebuilded pyside from qt.io, support x64 on python2.7
                os.system((
                    '%s -m pip install '
                    '--index-url=http://download.qt.io/snapshots/ci/pyside/5.11/latest/ '
                    'pyside2 --trusted-host download.qt.io') % sys.executable)
        else:
            # Support win32 on python2.7
            install_requires.append('PySide==1.2.4')
    else:
        install_requires.append('PySide==1.2.2')

setup_requires = [
    'pytest-runner',
    # TODO(starofrainnight): put setup requirements (distutils extensions, etc.) here
]

tests_requires = [
    'pytest',
    # TODO: put package test requirements here
]

description = (
    "Automatic install a qt binding (pyside/pyside2/pyqt/pyqt5) "
    "that could install in the runtime environment")

setup(
    name='install-qt-binding',
    version='0.0.8',
    description=description,
    long_description=long_description,
    author="Hong-She Liang",
    author_email='starofrainnight@gmail.com',
    url='https://github.com/starofrainnight/install-qt-binding',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    license="Apache Software License",
    zip_safe=False,
    keywords='installqtbinding,install-qt-binding',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=tests_requires,
    setup_requires=setup_requires,
)
