#!/usr/bin/env python
import setuptools

from pykit import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as fh:
    install_requires=[line.strip('\n') for line in fh.readlines() if line.strip() and not line.strip().startswith('#')]

setuptools.setup(
    name='pykit-bsc',
    version=__version__,
    description='A collection of toolkit lib for distributed system development in python',
    long_description=long_description,
    url='https://github.com/bsc-s2/pykit',
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    license='MIT',
    long_description_content_type='text/markdown',
    packages=['pykit'],
    install_requires=install_requires,
    python_requires='>=2.7',
    classifiers=(
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
