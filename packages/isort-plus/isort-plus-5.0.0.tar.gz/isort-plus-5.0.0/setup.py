#!/usr/bin/env python

import subprocess
import sys

try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand

    class PyTest(TestCommand):
        extra_kwargs = {'tests_require': ['pytest', 'mock']}

        def finalize_options(self):
            TestCommand.finalize_options(self)
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            import pytest
            sys.exit(pytest.main(self.test_args))

except ImportError:
    from distutils.core import setup, Command

    class PyTest(Command):
        extra_kwargs = {}
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            raise SystemExit(subprocess.call([sys.executable, 'runtests.py']))

with open('README.rst', 'r') as f:
    readme = f.read()

setup(name='isort-plus',
      version='5.0.0',
      description='isort fork this requirements.txt and Pipfile support',
      long_description=readme,
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='https://github.com/orsinium/isort',
      license="MIT",
      entry_points={
        'console_scripts': [
            'isort = isort.main:main',
        ],
        'distutils.commands': ['isort = isort.main:ISortCommand'],
        'pylama.linter': ['isort = isort.pylama_isort:Linter'],
      },
      packages=['isort'],
      extras_require={
          'requirements': ['pip', 'pipreqs'],
          'pipfile': ['pipreqs', 'requirementslib'],
      },
      install_requires=['futures; python_version < "3.2"'],
      python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
      cmdclass={'test': PyTest},
      keywords='Refactor, Python, Python2, Python3, Refactoring, Imports, Sort, Clean',
      classifiers=['Development Status :: 6 - Mature',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Programming Language :: Python :: Implementation :: PyPy',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'],
      **PyTest.extra_kwargs)
