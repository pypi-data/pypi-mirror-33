#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

setup(
    name='robobrowserquery',
    version='0.6.9',
    description='PyQuery on RoboBrowser',
    license='BSD',
    author='ytyng',
    author_email='ytyng@live.jp',
    url='https://github.com/ytyng/robobrowserquery.git',
    keywords='RoboBrowser, PyQuery, Browser, Scraping',
    packages=['robobrowserquery'],
    install_requires=['robobrowser', 'pyquery'],
    # install_requires=[
    #   'git+https://github.com/M157q/robobrowser/', 'pyquery'],
    entry_points={
    },
)
