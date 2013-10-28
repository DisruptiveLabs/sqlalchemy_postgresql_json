""" sqlalchemy-postgresql-json
	Adds JSON support to SQLAlchemy, with magic helpers to keep things mutable
"""

from setuptools import setup, find_packages
from git_version import get_git_version

setup(
    name='sqlalchemy_postgresql_json',
    version=get_git_version(),
    long_description=__doc__,
    py_modules=['postgres_json'],
    include_package_data=True,
    scripts=['git_version.py'],
    zip_safe=False,
    install_requires=['psycopg2', 'sqlalchemy'])
