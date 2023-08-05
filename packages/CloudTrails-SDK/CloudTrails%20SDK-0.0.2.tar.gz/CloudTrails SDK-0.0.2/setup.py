import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CloudTrails SDK",
    version="0.0.2",
    author="Yaisel Hurtado, Raydel Miranda",
    author_email="hurta2yaisel@gmail.com, raydel.miranda.gomez@gmail.com",
    description="SDK for CloudTrails DevOps management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/elasbit/fc-cloudtrails-sdk-py/src/develop/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ),
)
