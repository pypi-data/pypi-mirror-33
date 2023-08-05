# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='eprocess',
    version='0.5',
    description='A lightweight library that help to process, slice and filter a lot of data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/eliosf27/eprocess.git',
    author='Elio Rincón',
    author_email='eliosf27@gmail.com',
    license='MIT',
    packages=['eprocess'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
