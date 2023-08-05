==================
install-qt-binding
==================


.. image:: https://img.shields.io/pypi/v/install-qt-binding.svg
    :target: https://pypi.python.org/pypi/install-qt-binding

.. image:: https://travis-ci.org/starofrainnight/install-qt-binding.svg
    :target: https://travis-ci.org/starofrainnight/install-qt-binding.html

.. image:: https://ci.appveyor.com/api/projects/status/github/starofrainnight/install-qt-binding?svg=true
    :target: https://ci.appveyor.com/project/starofrainnight/install-qt-binding

Automatic choice and install a qt binding (pyside/pyside2/pyqt/pyqt5) that
could install in current runtime environment.

Anyway, we will try to install pyside if we can, otherwise pyqt* will be
installed as fallbacks due to their different licenses.

* License: Apache-2.0

Usage
---------

Just place 'install-qt-binding' to your install_requires list in setup(), see
sample below

.. code ::

    from setuptools import setup, find_packages

    install_requires = [
        'install-qt-binding',
    ]

    setup(
        name='testlib',
        version='0.0.1',
        description="Just for test",
        long_description=long_description,
        author="Hong-She Liang",
        author_email='starofrainnight@gmail.com',
        url='https://github.com/starofrainnight/testlib',
        packages=find_packages(),
        include_package_data=True,
        install_requires=install_requires,
        license="Apache Software License",
        zip_safe=False,
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
    )

Credits
---------

This package was created with Cookiecutter_ and the `PyPackageTemplate`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`PyPackageTemplate`: https://github.com/starofrainnight/rtpl-pypackage

