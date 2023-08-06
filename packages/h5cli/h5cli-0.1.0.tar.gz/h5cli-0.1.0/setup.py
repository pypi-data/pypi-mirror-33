#! /usr/bin/env python3

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "h5cli/VERSION")) as f:
    version = f.read().strip()

with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()


setup(
    name="h5cli",
    packages=find_packages(),
    package_data={"h5cli": ["VERSION"]},
    python_requires=">=3.5",
    install_requires=["h5py>=2.7.0", "cmd2>=0.9.2", "tree_format"],
    extras_require={"dev": ["black", "pre-commit"]},
    version=version,
    description="bash-like iterface for HDF5 files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/h5cli/h5cli",
    author="Kyle Sunden",
    author_email="sunden@wisc.edu",
    license="MIT",
    entry_points={"console_scripts": ["h5cli=h5cli.cli:main"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ],
    project_urls={
        "Bug Reports": "https://gitlab.com/h5cli/h5cli/issues",
        "Gitter": "https://gitter.im/h5cli/Lobby",
        "Source": "https://gitlab.com/h5cli/h5cli",
    },
)
