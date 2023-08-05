from setuptools import setup, find_packages
# To use a consistent encoding
from os import path
import codecs
import fab_geoalchemy

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codecs.open('README.rst') as f:
    long_description = f.read()

extras = {
    'test': ['pytest', 'pytest-cov']
}


setup(
    name="fab_geoalchemy",
    version=fab_geoalchemy.__version__,
    description="Plugin to implement Geoalchemy fields in Flask Appbuilder",
    long_description=long_description,
    url="https://github.com/dolfandringa/fab_geoalchemy",
    author="Dolf Andringa",
    author_email="dolfandringa@gmail.com",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['psycopg2', 'sqlalchemy', 'flask_appbuilder',
                      'geoalchemy2'],
    setup_requires=['pytest-runner', 'm2r'],
    tests_require=extras['test'],
    extras_require=extras,
    project_urls={
        'Source': 'https://github.com/dolfandringa/fab_geoalchemy/'
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: MIT License'
    ],
    keywords='gis sqlalchemy'
)
