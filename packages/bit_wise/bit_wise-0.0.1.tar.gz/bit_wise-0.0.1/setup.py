import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bit_wise",
    version="0.0.1",
    author="DataScienceStep",
    author_email="DataScienceStep@GMail.com",
    description="Bitwise functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DataScienceStep/bit",
    packages=setuptools.find_packages(),
    
)