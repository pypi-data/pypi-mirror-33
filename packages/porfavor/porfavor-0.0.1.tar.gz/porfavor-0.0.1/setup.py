import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="porfavor",
    version="0.0.1",
    author="osherdp",
    author_email="osherdepaz@gmail.com",
    description="Releasing Sphinx documentation the easy way",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/osherdp/porfavor",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
