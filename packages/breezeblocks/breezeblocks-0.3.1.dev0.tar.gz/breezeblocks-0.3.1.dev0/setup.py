import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'package'))
from breezeblocks import __version__ as bb_version
sys.path.pop(0)

from setuptools import setup
from setuptools import find_packages

with open('README.rst', 'r') as f:
    long_description=f.read()

setup(name='breezeblocks',
    version=bb_version,
    description='A lightweight SQL Querying package.',
    author='Quinn Mortimer',
    author_email='quinn.e.mortimer@gmail.com',
    url='https://github.com/modimore/BreezeBlocks',
    license='MIT',
    packages=find_packages('package'),
    package_dir={ '': 'package' },
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent"
    ]
)
