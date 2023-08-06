"""
Mongo-Migrations
-------------

Provides possibility to create and manage migrations for MongoDB.
"""
from setuptools import setup


setup(
    name='mongo-migrations',
    version='0.2.4',
    url='https://bitbucket.org/submax82/mongo_migrations',
    license='BSD',
    author='Massimo Cavalleri',
    author_email='submax@tiscali.it',
    description='Provides possibility to create and manage migrations for MongoDB',
    long_description=__doc__,
    packages=['mongo_migrations'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'pymongo',
        'click'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest-cov', 'pytest', 'mock'],
    entry_points={
        'console_scripts': ['mongomigrations = mongo_migrations.commands:main'],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
