import setuptools
from m2r import convert

with open("README.md", "r") as f:
    long_description = convert(f.read())

setuptools.setup(
    name="chromaprint",
    version="0.5",
    author="NoSmokingBandit",
    author_email="nosmokingbandit@gmail.com",
    description="Small package to facilitate colored terminal output.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/nosmokingbandit/chromaprint",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
