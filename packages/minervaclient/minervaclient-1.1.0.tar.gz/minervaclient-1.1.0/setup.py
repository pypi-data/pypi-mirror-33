#!/usr/bin/env python

from setuptools import setup
# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='minervaclient',
    version='1.1.0',
    description='Tools and Utilities that can be used to access McGill University\'s Minerva service',
    author='Ryan B Au',
    author_email='auryan898@gmail.com',
    url='https://github.com/auryan898/minervaclient',
    download_url='https://github.com/auryan898/minervaclient/archive/master.zip',
    keywords=['minerva','banner','mcgill','college','schedule'],
    packages=['minervaclient'],
    scripts=['scripts/minervac'],
    classifiers=[],
    install_requires=[
        'requests', 'beautifulsoup4', 'html5lib'
    ],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown'
     )
