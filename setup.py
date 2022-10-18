from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='dbca',
   version='1.0',
   description='distribution-based compositionality assessment',
   license="MIT",
   long_description=long_description,
   author='Ronen Tamari',
   packages=['dbca'],  #same as name
   install_requires=['networkx'], #external packages as dependencies
)
