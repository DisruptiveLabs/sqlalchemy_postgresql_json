""" sqlalchemy_postgresql_json
	Adds JSON support to SQLAlchemy, with magic helpers to keep things mutable
"""

from setuptools import setup, find_packages
from sqlalchemy_postgresql_json import __version__

setup(
    name='sqlalchemy-postgresql-json',
    version=".".join(map(str, __version__)),
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['psycopg2', 'sqlalchemy'])
