import os
from setuptools import setup, find_packages
from p3mail import consts

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name=consts.prg_name,
    version="0.1.1",
    author="Gary Marigliano",
    author_email="gary-pypi@marigliano.ch",
    description=(consts.full_prg_name),
    keywords="mail pipe stdin",
    url="https://github.com/krypty/p3mail",
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'p3mail=p3mail.p3mail:main'
        ],
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
    ],
)
