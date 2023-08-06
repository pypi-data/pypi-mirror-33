from setuptools import setup, find_packages

import allgo

setup(
    name='allgo',
    version=allgo.__version__,
    packages=find_packages(),
    author="Sebastien Campion",
    author_email="sebastien.campion@inria.fr",
    description="AllGo client module",
    long_description=open('README.md').read(),
    include_package_data=True,
    url='https://gitlab.inria.fr/allgo/client',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications",
    ],
    license="AGPL",
)