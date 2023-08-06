#!/usr/bin/python3

from setuptools import setup
with open("./.VERSION") as f: ver = f.readline()
setup(name="clusterplot",
        version=ver,
      description="a self-similarity filter for big datasets",
      long_description=open('README.md').read(),
      url="https://www.github.com/fmegg/clusterplot/",
      author="Felix Meggendorfer, Carlos Palma, Willi Auwaerter",
      author_email="felix.meggendorfer@tum.de",
      license="Apache-v2.0",
      install_requires=[
          "numpy",
          "networkx"]
      )
