import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spinfo",
    version="1",
    author="Ziyadsk",
    author_email="ziyadkader@outlook.com",
    description="command line utility for information about projects",
    #url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)