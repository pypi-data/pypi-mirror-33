"""Packaging settings."""


from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=gpr1dfusion.py', '--cov-report=term-missing',
                      '--ignore=lib/'])
        raise SystemExit(errno)


setup(
    name = 'gpr1dfusion',
    version = '1.0.0',
    description = 'Classes for Gaussian Process Regression fitting of 1D fusion data with errorbars, built on GPR1D package.',
    long_description = long_description,
    url = 'https://gitlab.com/aaronkho/gpr1dfusion.git',
    author = 'Aaron Ho',
    author_email = 'a.ho@differ.nl',
    license = 'MIT',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'
    ],
    keywords = 'gaussian process regression, 1D data fitting, kriging, OMFIT, fusion data',
    py_modules = ['gpr1dfusion'],
    scripts = [],
    install_requires = ['GPR1D>=1.0.1', 'numpy'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    cmdclass = {'test': RunTests},
)
