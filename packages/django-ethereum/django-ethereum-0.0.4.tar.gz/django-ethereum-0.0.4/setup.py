import os
import subprocess
import sys

from setuptools import (
    find_packages,
    setup,
)
from setuptools.command.install import (
    install,
)

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

VERSION = "0.0.4"


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = subprocess.check_output(['git', 'describe', '--tags']).decode().rstrip('\n')

        if tag != 'v{}'.format(VERSION):
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setup(
    name='django-ethereum',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Utilities to make it easier to work with Ethereum from your Django app.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/mikery/django-ethereum/',
    author='Mike Ryan',
    author_email='mike@backtothelab.io',
    classifiers=[
    ],
    cmdclass={
        'verify_git_tag': VerifyVersionCommand,
    }
)
