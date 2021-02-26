#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    author="Mark Ward",
    author_email='markmaw@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Split large XML files into small XML files",
    entry_points={
        'console_scripts': [
            'xmlsplitter=xmlsplitter.cli:main',
        ],
    },
    install_requires=[],
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='xmlsplitter',
    name='xmlsplitter',
    packages=find_packages(include=['xmlsplitter', 'xmlsplitter.*']),
    url='https://github.com/MarkAWard/xmlsplitter',
    version='0.0.0',
    zip_safe=False,
)
