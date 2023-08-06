import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BGAutoStocks",
    version="0.0.1",
    author="Brendan Greenlee",
    author_email="greenlbt@miamioh.edu",
    description="An automated stock trading virtual environment via google sheets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
