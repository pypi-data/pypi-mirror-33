# -*- coding: utf-8 -*-
import os
from distutils.core import setup

README_RST = os.path.join(os.path.dirname(__file__), 'README.txt')
with open(README_RST) as readme:
    long_description = readme.read()

setup(
    name='libthither',
    version='0.10.2',
    description='Python Library for Thither.Direct',
    long_description=long_description,

    url='https://thither.direct/information/services/commercial/index',
    license='MIT',
    package_dir={'libthither': 'libthither'},
    packages=['libthither',
              'libthither.api'],

    maintainer='Kashirin Alex',
    maintainer_email='kashirin.alex@gmail.com',

    classifiers=(
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Customer Service",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: Log Analysis",
        "License :: OSI Approved :: MIT License",
    ),
    platforms=['any'],
)
