#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from distutils import log
from setuptools import setup, find_packages


name = "dronedirector"
description = "A simple Python package for simulating aerial drones"
readme = "README.md"
requirements = "requirements.txt"
verfile = "_version.py"
root = os.path.dirname(os.path.abspath(__file__))
log.set_verbosity(log.DEBUG)
try:
    import pypandoc
    long_description = pypandoc.convert(readme, "rst")
except ImportError:
    with open(readme) as f:
        long_description = f.read()
with open(requirements) as f:
    dependencies = f.read().splitlines()
with open(os.path.join(root, name, verfile)) as f:
    v = f.readlines()[-2]
    v = v.split('=')[1].strip()[1:-1]
    version = '.'.join(v.replace(" ", "").split(","))


setup_args = {
    'name': name,
    'version': version,
    'description': description,
    'long_description': long_description,
    'install_requires': dependencies,
    'packages': find_packages(),
    'license': "Apache License Version 2.0",
    'author': "Alex Marchenko",
    'author_email': "alexvmarch@gmail.com",
    'maintainer_email': "alexvmarch@gmail.com",
    'url': "https://github.com/avmarchenko/" + name,
    'download_url': "https://github.com/avmarchenko/{}/archive/v{}.tar.gz".format(name, version)
}

setup(**setup_args)
