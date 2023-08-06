import re
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def read_module_contents():
    with open('helga_bugzilla/__init__.py') as init:
        return init.read()


module_file = read_module_contents()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
version = metadata['version']


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main('helga_bugzilla/tests', self.pytest_args)
        sys.exit(errno)

setup(name="helga-bugzilla",
      version=version,
      description=('bugzilla plugin for helga'),
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Bug Tracking',
                   ],
      keywords='irc bot bugzilla',
      author='ken dreyer',
      author_email='ktdreyer@ktdreyer.com',
      url='https://github.com/ktdreyer/helga-bugzilla',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'helga',
          'txbugzilla>=1.4.0',
      ],
      tests_require=[
          'pytest',
      ],
      entry_points=dict(
          helga_plugins=[
              'bugzilla = helga_bugzilla:helga_bugzilla',
          ],
      ),
      cmdclass = {'test': PyTest},
)
