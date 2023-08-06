#!/usr/bin/python3

from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="dev-pipeline-build",
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
            'build = devpipeline_build.build:_BUILD_COMMAND'
        ],

        'devpipeline.builders': [
            'nothing = devpipeline_build.builder:_NOTHING_BUILDER',
        ]
    },

    author="Stephen Newell",
    description="build tooling for dev-pipeline",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-build",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities"
    ]
)
