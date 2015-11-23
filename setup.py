#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
setuptools.setup(setup_requires=['pbr'], pbr=True)

# try:
#     from setuptools import setup
# except ImportError:
#     from distutils.core import setup

# setup(
#     name="quepy-ko",
#     version="0.3",
#     description="Quepy fork for Korean language and SPARQL constraint support",
#     long_description=open('README.rst').read(),
#     author="Baeg-il Kim",
#     author_email="cedar101@gmail.com",
#     url="https://github.com/cedar101/quepy-ko",
#     keywords=["regular expressions", "regexp", "re", "NLP",
#               "natural language processing",
#               "natural language interface to database", "sparql", "database",
#               "interface", "quepy", "quepy-ko", "Korean", "Korean language"],
#     classifiers=[
#         "Programming Language :: Python",
#         "Development Status :: 3 - Alpha",
#         "Intended Audience :: Developers",
#         "Natural Language :: Korean",
#         "License :: OSI Approved :: BSD License",
#         "Operating System :: OS Independent",
#         "Topic :: Database",
#         "Topic :: Scientific/Engineering :: Human Machine Interfaces",
#         "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
#         "Topic :: Software Development :: Libraries :: Application Frameworks",
#         "Topic :: Text Processing :: Linguistic",
#         "Topic :: Text Processing",
#         "Topic :: Utilities",
#     ],
#     packages=["quepy-ko"],
#     install_requires=["refo", "nltk", "SPARQLWrapper", "docopt", "natto-py"],
#     scripts=["scripts/quepy"]
# )
