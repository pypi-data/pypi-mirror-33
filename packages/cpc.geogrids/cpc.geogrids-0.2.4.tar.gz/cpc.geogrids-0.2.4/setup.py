#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

requirements = ['scipy', 'cpc.stats']

setup(
    name="cpc.geogrids",
    version='v0.2.4',
    description="CPC geospatial grids (grid definitions, interpolation, etc.)",
    long_description=readme + '\n\n' + history,
    author="Mike Charles",
    author_email='mike.charles@noaa.gov',
    url="https://github.com/noaa-nws-cpc/cpc.geogrids",
    packages=find_packages(),
    namespace_packages=['cpc'],
    include_package_data=True,
    install_requires=requirements,
    tests_require = ['pytest', 'pytest-cov'],
    license="CC",
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    ],
)
