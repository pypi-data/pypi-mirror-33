import setuptools
from setuptools import find_packages

setuptools.setup(
    name="chaotestpackage",
    version="0.0.3",
    author="peter wang",
    author_email="peter@dashbase.io",
    description="Dashbase python sdk",
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    install_requires=[
        "requests",
        "schematics"
    ]
)
