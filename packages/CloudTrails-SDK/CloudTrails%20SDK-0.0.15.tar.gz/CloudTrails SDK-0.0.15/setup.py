import os

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


VERSION = os.environ.get("TAG_VERSION")
VERSION = VERSION[2:] if VERSION else "0.0.15"

setuptools.setup(
    name="CloudTrails SDK",
    version=VERSION,
    author="Yaisel Hurtado, Raydel Miranda",
    author_email="hurta2yaisel@gmail.com, raydel.miranda.gomez@gmail.com",
    description="SDK for CloudTrails DevOps management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/elasbit/fc-cloudtrails-sdk-py",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ),
)
