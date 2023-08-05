#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from setuptools import setup, find_packages


requirements = ["pypinyin"]
if sys.version_info[:2] < (2, 7):
    requirements.append('argparse')
if sys.version_info[:2] < (3, 4):
    requirements.append('enum34')
if sys.version_info[:2] < (3, 5):
    requirements.append('typing')

extras_require = {
    ':python_version<"2.7"': ['argparse'],
    ':python_version<"3.4"': ['enum34'],
    ':python_version<"3.5"': ['typing'],
}

setup(
    name="chrhyme",
    version="0.2.6",
    author="Jiajie Yan",
    author_email="jiaeyan@gmail.com",
    description="Find rhymes for Chinese words.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    license="MIT",
    url="https://github.com/jiaeyan/Chinese-Rhyme",
    keywords=['chinese', 'rhymes', 'rhythm', 'rap', 'rapper', 'hip-pop', 'poem'],
    packages=find_packages(),
    install_requires=requirements,
    extras_require=extras_require,
    python_requires='>=2.6, >=3',
    include_package_data=True,
    # package_data={
    #     'chrhyme': ['data/phrase_dict.txt', 'data/demo.png'],
    # },
    # data_files=[('chrhyme/data', ['chrhyme/data/phrase_dict.txt', 'chrhyme/data/demo.png'])],
    entry_points={
        'console_scripts': ['chrhyme = chrhyme.__main__:main']
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'Topic :: Text Processing',
    ]
)
