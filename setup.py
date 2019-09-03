# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:

'''

import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twless",
    version="0.0.2",
    author="konas",
    author_email="konasyan2009@gmail.com",
    description="a coroutine framework based on twisted and stackless python",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/konas/twless",
    install_requires=[
        "twisted",
    ],
    packages=['twless'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
