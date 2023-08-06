import os
import re
from setuptools import setup, find_packages


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


setup(
    name="django-extant-test-db",
    version=get_version('extant_test_db'),
    description=read('DESCRIPTION'),
    long_description=read('README.md'),
    author='Mjumbe Poe',
    author_email='mjumbewu@gmail.com',
    url="https://github.com/mjumbewu/django-extant-test-db",
    packages=find_packages(),
    include_package_data=True,
)