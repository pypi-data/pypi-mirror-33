from setuptools import setup, find_packages
# from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name="adaptationism",
    version="0.0.8",
    author="Jameson Lee",
    author_email="jameson.developer@gmail.com",
    description="Understand the features of language for different kinds of corpora",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamesonl/adaptationism",
    packages=find_packages(),
)
