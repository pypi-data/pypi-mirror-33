#!/usr/bin/python3

from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="dev-pipeline-bootstrap",
    version="0.2.0a0",
    package_dir={
        "": "lib"
    },
    packages=find_packages("lib"),

    install_requires=[
        'dev-pipeline-core >= 0.2.0a0',
        'dev-pipeline-build >= 0.2.0a0',
        'dev-pipeline-scm >= 0.2.0a0'
    ],

    entry_points={
        'devpipeline.drivers': [
            'bootstrap = devpipeline_bootstrap.bootstrap:_BOOTSTRAP_COMMAND'
        ]
    },

    author="Stephen Newell",
    description="build tooling for dev-pipeline",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-bootstrap",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities"
    ]
)
