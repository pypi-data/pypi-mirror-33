#!/usr/bin/env python

# Copyright Least Authority TFA GmbH
# See LICENSE for details.

import setuptools

_metadata = {}
with open("src/subunitreporter/_metadata.py") as f:
    exec(f.read(), _metadata)
with open("README.rst") as f:
    _metadata["description"] = f.read()

setuptools.setup(
    name="subunitreporter",
    version=_metadata["version_string"],
    description="A Twisted Trial reporter which emits Subunit v2 streams.",
    long_description=_metadata["description"],
    author="subunitreporter Developers",
    url="https://github.com/LeastAuthority/subunitreporter",
    license="MIT",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src") + ["twisted.plugins"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "zope.interface",
        "attrs",
        "testtools",
        "python-subunit",
        "twisted",
    ],
)
