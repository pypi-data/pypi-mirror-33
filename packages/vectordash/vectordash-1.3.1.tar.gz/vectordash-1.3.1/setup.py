#!/usr/bin/env python
import os
from setuptools import find_packages, setup

project = "vectordash"
version = "1.3.1"

# with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
#     long_description = readme.read()

long_description = "A command line tool for interacting with [Vectordash](http://vectordash.com) GPU instances. " \
                   "For a more detailed overview on how to get started, how the commands work, or general questions, " \
                   "please go to our [docs](https://docs.vectordash.com)!" \
                   "1) `vectordash secret <secret_token>` - update's the user's secret token which is used for " \
                   "authentication" \
                   "2) `vectordash list` - lists the machines the user can connect to; these are machines user is " \
                   "currently renting" \
                   "3) `vectordash ssh <machine_id>` - connect the user to a machine via SSH" \
                   "4) `vectordash push <machine_id> <from_path> <to_path>`" \
                   "This uses scp to push files to the machine. If `<to_path>` is not included, then `scp` pushes it " \
                   "to the machine's home directory." \
                   "5) `vectordash pull <machine_id> <from_path> <to_path>`" \
                   "Same command as above, except we're copying files from the machine to the local machine. " \
                   "If `<to_path>` is not provided, then copies the files to the current directory."

setup(
    name=project,
    version=version,
    description="Command line interface for interacting with Vectordash GPUs.",
    long_description=long_description,
    author="Arbaz Khatib",
    author_email="contact@vectordash.com",
    url="https://github.com/Vectordash/vectordash-cli",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="vectordash",
    install_requires=[
        "click>=6.7,<7",
        "requests>=2.18.4",
        "colored>=1.3.5",
    ],
    setup_requires=[],
    dependency_links=[],
    entry_points={
        "console_scripts": [
            "vectordash = vectordash.main:cli",
        ],
    },
)
