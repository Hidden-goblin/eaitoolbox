# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="eaiautomatontools",
    version="1.0.1",
    description="UI utilities in order to abstract selenium commands",
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        # 'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'selenium~=3.14',
        'Pillow>=6.0.0'
    ],
    python_requires='>=3.7, !=2.*',
    packages=find_packages(),
    include_package_data=True,
    author="Eric Aïvayan",
    author_email="eric.aivayan@free.fr"
)
