# -*- coding: utf-8 -*-


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="af",
    version="1.0.0",
    author="Laurent Bié",
    author_email="hloplol@gmail.com",
    description="Af format tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=['af'],
    install_requires=[
        'polyglot',
        'six',
        'pycld2',
        'PyICU',
        'PTable',
        'markdown',
        'tqdm',
        'chardet'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
    scripts=['bin/af2bilingual']
)



