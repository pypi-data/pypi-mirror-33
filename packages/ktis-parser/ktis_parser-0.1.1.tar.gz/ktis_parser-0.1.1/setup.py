import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ktis_parser",
    packages=['ktis_parser'],
    version="0.1.1",
    author="zaeval",
    author_email="zaeval@kookmin.ac.kr",
    description="ktis default information parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zaeval/ktis_parser",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)