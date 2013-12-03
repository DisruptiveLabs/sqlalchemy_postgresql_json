""" sqlalchemy_postgresql_json
	Adds JSON support to SQLAlchemy, with magic helpers to keep things mutable
	And now adds LTREE support as well
"""

from setuptools import setup, find_packages

setup(
    name='sqlalchemy-postgresql-json',
    version="0.4.1",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['psycopg2', 'sqlalchemy'])
