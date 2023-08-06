from setuptools import setup

import pandas_refract
import sys


if sys.version_info[0] >= 3:
    openf = open
else:
    import codecs

    openf = codecs.open


def read(fn):
    with openf(fn, encoding="utf-8") as fp:
        return fp.read()


setup(
    name="pandas_refract",
    version=pandas_refract.__version__,
    description="Split a dataframe by boolean array",
    long_description=(read("README.rst")),
    url="http://github.com/kdggavkc/pandas-refract/",
    license=pandas_refract.__license__,
    author=pandas_refract.__author__,
    author_email="nickclawrence@gmail.com",
    py_modules=["pandas_refract"],
    install_requires=[
        'numpy'
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
