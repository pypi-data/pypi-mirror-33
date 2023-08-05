import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="liburl",
    version="0.0.2",
    author="phyng",
    author_email="phyngk@gmail.com",
    description="A small package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://liburl.com",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
