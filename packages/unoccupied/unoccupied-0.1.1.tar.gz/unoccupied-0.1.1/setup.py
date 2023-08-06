#!/usr/bin/env python3

"""Install script."""

from setuptools import setup, find_packages
import src.unoccupied.info as info

with open('README.md', mode='r', encoding='utf8') as f:
    long_desc = f.read()

setup(
    name=info.PROJECT_NAME,
    version=info.VERSION_STR,
    author=info.AUTHOR,
    author_email=info.AUTHOR_EMAIL,
    license=info.LICENSE,
    url=info.PROJECT_URL,
    description=info.DESCRIPTION,
    long_description=long_desc,
    long_description_content_type='text/markdown',

    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest >=3.6, <4'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
)
