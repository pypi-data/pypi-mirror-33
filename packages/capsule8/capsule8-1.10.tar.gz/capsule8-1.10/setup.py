import os
from os import path
import sys
from setuptools import setup, Command
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -rf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README-PYPI.md')) as f:
    long_description = f.read()

setup(
    name='capsule8',
    version="1.10",
    description="capsule8 open source sensor python grpc bindings",
    author='Alexander Comerford',
    author_email='alex@capsule8.com',
    url='http://github.com/capsule8/api-python',
    install_requires=["grpcio",
                      "grpcio-tools",
                      "google-api-python-client",
                      "googleapis-common-protos"],
    test_requires=["pytest"],
    packages=["capsule8", "capsule8.api", "capsule8.api.v0"],
    cmdclass={
        'clean': CleanCommand,
        'test': PyTest
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True
)
