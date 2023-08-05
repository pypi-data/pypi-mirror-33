#!/usr/bin/env python2
import setuptools
import platform
import os
with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires     = ['ipython', ]

if platform.system() == "Windows":
    script_list =[os.path.join('shpy',"shpy.bat")]
else:
    script_list =[os.path.join('shpy',"shpy")]

setuptools.setup(
    name                 = 'shpy',
    python_requires      = '~=2.7',
    version              = '1',
    description          = "Make your shell python supportive.",
    long_description=long_description,
    scripts=script_list,
    packages=setuptools.find_packages(),
    author               = "ZviWex.",
    author_email         = "zvikizviki@gmail.com",
    url                  = 'https://ZviWex.com',
    install_requires     = install_requires,
    license              = "GNU",
    classifiers=(
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ),
)