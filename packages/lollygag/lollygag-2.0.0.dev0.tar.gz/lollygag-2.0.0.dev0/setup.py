#!/usr/bin/env python

import os
import sys

from setuptools.command.install import install
from setuptools import setup, find_packages

try:
    from setuptools_rust import RustExtension, Binding
except ImportError:
    import subprocess
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'setuptools_rust'])
    from setuptools_rust import RustExtension, Binding

VERSION = '2.0.0-dev'
DEPENDENCIES = ['requests>=2.2.1']
TEST_DEPENDENCIES = ['pytest']


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = f"Git tag: {tag} does not match the version of this app: {VERSION}"
            sys.exit(info)


if __name__ == '__main__':
    setup(
        name='lollygag',
        author='Daniel Kiss',
        version=VERSION,
        author_email='littlesnorrboy@gmail.com',
        url='https://github.com/snorrwe/lollygag',
        description="A simple web crawling module",
        license="MIT",
        package_dir={'': 'src'},
        packages=find_packages('src'),
        install_requires=DEPENDENCIES,
        rust_extensions=[
            RustExtension(
                'lollygag_ext',
                'lollygag_ext/py_interface/Cargo.toml',
                binding=Binding.RustCPython)
        ],
        tests_require=TEST_DEPENDENCIES,
        extras_require={'ci': TEST_DEPENDENCIES},
        python_requires='>=3',
        cmdclass={
            'verify': VerifyVersionCommand,
        },
        zip_safe=False,
        include_package_data=True,
    )
