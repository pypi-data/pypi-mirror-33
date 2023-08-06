#!/usr/bin/python3

from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="dev-pipeline-scm",
    version="0.2.0a0",
    package_dir={
        "": "lib"
    },
    packages=find_packages("lib"),

    install_requires=[
        'dev-pipeline-core >= 0.2.0a0'
    ],

    entry_points={
        'devpipeline.drivers': [
            'checkout = devpipeline_scm.checkout:_SCM_COMMAND'
        ],

        'devpipeline.scms': [
            'nothing = devpipeline_scm.scm:_NOTHING_SCM',
        ]
    },

    author="Stephen Newell",
    description="scm tooling for dev-pipeline",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-scm",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities"
    ]
)
