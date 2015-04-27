""" sqlalchemy_postgresql_json
	Adds JSON support to SQLAlchemy, with magic helpers to keep things mutable
	And now adds LTREE support as well
"""

from setuptools import setup, find_packages

setup(
    name='sqlalchemy-postgresql-json',
    author="Franklyn Tackitt",
    author_email="franklyn@tackitt.net",
    url="https://github.com/DisruptiveLabs/sqlalchemy_postgresql_json",
    download_url="https://github.com/DisruptiveLabs/sqlalchemy_postgresql_json/tarball/0.4.4",
    version="0.4.5",
    description="Postgresql JSON Extension for sqlalchemy",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['psycopg2', 'sqlalchemy'])
