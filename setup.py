#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='donghua-downloader',
    version='1.0.0',
    author='DonghuaWorld Downloader',
    description='Download videos from donghuaworld.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/donghua-downloader',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'curl_cffi>=0.5.0',
    ],
    entry_points={
        'console_scripts': [
            'donghua-download=donghua_downloader:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)