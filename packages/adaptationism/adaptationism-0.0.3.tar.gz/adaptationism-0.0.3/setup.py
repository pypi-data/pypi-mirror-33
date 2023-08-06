from setuptools import setup, find_packages
# from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="adaptationism",
    version="0.0.3",
    author="Jameson Lee",
    author_email="jameson.developer@gmail.com",
    description="Useful NLTK toolkit for understanding.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamesonl/adaptationism",
    packages=find_packages(),
)
