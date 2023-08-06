import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pychecklist",
    version = "0.1.0",
    author = "Dylan Stephano-Shachter",
    author_email = "dstephanoshachter@gmail.com",
    description = ("A simple program for keeping track of tasks."),
    license = "GPLv3",
    url = "https://github.com/dstathis/checklist/",
    packages=['checklist'],
    scripts=['bin/checklist'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    install_requires=['pptree'],
    python_requires='>=3',
)
