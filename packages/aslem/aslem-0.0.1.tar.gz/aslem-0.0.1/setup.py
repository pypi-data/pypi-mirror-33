import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aslem",
    version="0.0.1",
    author="Boris Ivanovic",
    author_email="borisi@stanford.edu",
    description="A lightweight experiment manager based on Linux's screen utility.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StanfordASL/aslem",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
