import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="environexus",
    version="1.0",
    author="Thomas Basche",
    author_email="tcbasche@gmail.com",
    description="A library for Home Assistant to manage Zwave devices on the Environexus controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tombasche/environexus",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)