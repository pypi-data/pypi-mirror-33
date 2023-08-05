"""
Setup script for proxi.

You can install proxi with

python setup.py install
"""
import io
import re
from setuptools import setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('proxi/algorithms/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='Proxi',
    version=version,
    url='http://ailab.ist.psu.edu/yasser/',
    license='BSD',
    author='Yasser El-Manzalawy',
    author_email='yasser@idsrlab.com',
    maintainer='Yasser El-Manzalawy',
    maintainer_email='yasser@idsrlab.com',
    description='Python Library for Proximity Network Inference.',
    long_description=readme,
    packages=['proxi.algorithms', 'proxi.utils'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'scikit-learn',
        'networkx'
    ]

)