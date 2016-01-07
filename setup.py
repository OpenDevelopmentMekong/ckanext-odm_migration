from setuptools import setup, find_packages
import sys, os

version = '1.0.5'

setup(
    name='ckanext-odm_migration',
    version=version,
    description="OD Mekong CKAN's migration extension",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Alex Corbi',
    author_email='alex@open-steps.org',
    url='http://www.open-steps.org',
    license='AGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        odm_migration=ckanext.odm_migration.plugin:OdmMigrationPlugin
    ''',
)
