#!/usr/bin/env python
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name="py_redis_simple_queue",
    version="0.0.3",
    author="Lucas Coutinho",
    author_email="lrclucas@gmail.com",
    description="A simple but useful redis queue/worker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucasrc/py_redis_simple_queue",
    install_requires=['redis==2.10.6'],
    packages=setuptools.find_packages(exclude=['build', 'dist', 'test*']),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
