# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

_package_data = dict(
    full_package_name='develop',
    version_info=(0, 1, 0),
    __version__='0.1.0',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    description='tool to develop python packages',
    # keywords="",
    entry_points='dv=develop.__main__:main',
    # entry_points=None,
    license='MIT',
    since=2017,
    # status="α|β|stable",  # the package status on PyPI
    # data_files="",
    # universal=True,
    install_requires=[
        'ruamel.appconfig',
        'ruamel.std.argparse>=0.8',
    ],
)


version_info = _package_data['version_info']
__version__ = _package_data['__version__']
