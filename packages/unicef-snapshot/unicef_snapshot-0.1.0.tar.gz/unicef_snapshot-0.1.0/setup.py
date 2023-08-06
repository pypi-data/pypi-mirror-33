#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import codecs
import os.path
import re
import sys
from codecs import open
from setuptools import setup, find_packages
from setuptools.command.install import install

ROOT = os.path.realpath(os.path.dirname(__file__))
init = os.path.join(ROOT, 'src', 'unicef_snapshot', '__init__.py')
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

sys.path.insert(0, os.path.join(ROOT, 'src'))

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    VERSION = str(ast.literal_eval(_version_re.search(content).group(1)))
    NAME = str(ast.literal_eval(_name_re.search(content).group(1)))


def read(*files):
    content = []
    for f in files:
        content.extend(codecs.open(os.path.join(ROOT, 'src', 'requirements', f), 'r').readlines())
    return "\n".join(filter(lambda l:not l.startswith('-'), content))


install_requires = read('install.pip'),
tests_requires = read('install.pip', 'testing.pip')

# pfile = Project(chdir=False).parsed_pipfile
# install_requires = convert_deps_to_pip(pfile['packages'], r=False)
# tests_requires = convert_deps_to_pip(pfile['dev-packages'], r=False)


class VerifyTagVersion(install):
    """Verify that the git tag matches version"""

    def run(self):
        tag = os.getenv("CIRCLE_TAG")
        if tag != VERSION:
            info = "Git tag: {} does not match the version of this app: {}".format(
                tag,
                VERSION
            )
            sys.exit(info)


setup(name=NAME,
      version=VERSION,
      url='https://github.com/unicef/unicef-snapshot',
      author='UNICEF',
      author_email='dev@unicef.org',
      license="Apache 2 License",
      description='Snapshot of data changes in django models',
      long_description=codecs.open('README.md').read(),
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      include_package_data=True,
      install_requires=install_requires,
      extras_require={
          'test': tests_requires,
      },
      platforms=['any'],
      classifiers=[
          'Environment :: Web Environment',
          'Programming Language :: Python :: 3.6',
          'Framework :: Django',
          'Intended Audience :: Developers'],
      scripts=[],
      cmdclass={
          "verify": VerifyTagVersion,
      }
)
