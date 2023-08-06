#!/usr/bin/env python

from setuptools import setup, find_packages

version = '1.0.0'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='Valifor',
    version=version,
    description='A small validator for formats in the NCBI context',
    long_description=readme,
    keywords=['validator', 'formats', 'bioinformatics', 'fasta', 'fastq'],
    author='Najia Ahmadi and Alexander Ott',
    author_email="a.ott@student.uni-tuebingen.de",
    url="https://github.com/qbicsoftware/dmqb-grp1-2018",
    license=license,
    scripts=['scripts/valifor'],  # entry point! name of the script also sets name of the command in the cmd-line.
    install_requires=required,
    packages=find_packages(exclude='docs'),
    include_package_data=True
)
