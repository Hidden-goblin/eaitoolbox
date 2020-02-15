# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="eaitoolbox",
    version="1.0.0",
    description="General tools for automation",
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
        # 'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'requests',
        'xlsxwriter',
        'python-docx',
        'behave',
        'six',
        'dpath',
        'selenium~=3.14',
        'Pillow>=6.0.0'
    ],
    dependency_links=[],
    python_requires='>=3.7, !=2.*',
    packages=find_packages(),
    include_package_data=True,
    author="Eric Aïvayan",
    author_email="aivayan.erc@free.fr",
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-coverage"]
)
