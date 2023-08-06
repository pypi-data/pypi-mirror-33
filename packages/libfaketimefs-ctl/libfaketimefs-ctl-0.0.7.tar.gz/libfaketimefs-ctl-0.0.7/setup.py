#!/usr/bin/env python

from setuptools import setup

setup(
    name='libfaketimefs-ctl',
    version='0.0.7',
    description='libfaketimefs controller',
    author='Raymond Butcher',
    author_email='ray.butcher@claranet.uk',
    url='https://github.com/claranet/libfaketimefs-ctl',
    license='MIT License',
    packages=(
        'libfaketimefs_ctl',
    ),
    scripts=(
        'bin/libfaketimefs-ctl',
    ),
    install_requires=(
        'boto3',
        'libfaketimefs-botocore',
        'py-dateutil',
    ),
)
