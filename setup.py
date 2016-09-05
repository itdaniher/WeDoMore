#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='wedo',
    version='1.1.0',
    packages=find_packages(),
    install_requires=['pyusb'],
    zip_safe=False,
    include_package_data=True,
    author="Guillaume BINET",
    author_email="gbin@gootz.net",
    description="This is a python library for the Lego WeDo, a tethered-over-USB sensing and robotics toolkit produced by Lego for the educational market.",
    long_description=''.join([read('README.rst'), '\n\n', read('CHANGES.rst')]),
    license="GPL",
    keywords="lego wedo motor tilt sensor driver",
    url="https://github.com/gbin/WeDoMore",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2"]
)
