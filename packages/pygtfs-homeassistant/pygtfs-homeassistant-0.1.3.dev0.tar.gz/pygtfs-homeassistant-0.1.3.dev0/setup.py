import codecs
import os.path

from setuptools import setup, find_packages

readme = os.path.join(os.path.dirname(__file__), 'README.md')
with codecs.open(readme, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pygtfs-homeassistant',
    version="0.1.3.dev0",
    author='Yaron de Leeuw',
    author_email="me@jarondl.net",
    description='Models GTFS data in a database.',
    long_description='This package is created from https://github.com/robbiet480/pygtfs/archive/00546724e4bbcb3053110d844ca44e2246267dd8.zip#pygtfs==0.1.3 No updates are expected.',
    license='MIT',
    keywords='gtfs',
    url='https://github.com/jarondl/pygtfs',
    packages=find_packages(),
    install_requires=['sqlalchemy>=0.7.8',
                      'pytz>=2012d',
                      'six',
                      'docopt'
                      ],
    tests_require=['nose'],
    test_suite='nose.collector',
    entry_points={'console_scripts': ['gtfs2db = pygtfs.gtfs2db:main']},
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
        ]
)
