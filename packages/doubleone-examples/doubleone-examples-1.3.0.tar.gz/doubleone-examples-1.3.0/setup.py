import setuptools 
with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="doubleone-examples",
    version="1.3.0",
    author="Example Author",
    description="A small example package",
    packages=setuptools.find_packages(),
)
"""from distutils.core import setup
setup(
name = 'doubleone-examples',
version = '1.1.0',
py_modules = ['nester'],
author = '11',
author_email = 'doubleone@outlook.com',
url = 'http//www.11.com',
description = 'A simple printer of nested list'
)
"""