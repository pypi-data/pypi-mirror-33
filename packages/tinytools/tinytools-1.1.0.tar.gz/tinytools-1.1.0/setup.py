#from distutils.core import setup
from setuptools import setup, find_packages

install_requires = [
    'numpy'
    ]

# import __version__
exec(open('tinytools/_version.py').read())

setup(
    name='tinytools',
    version=__version__,
    author='Nathan Longbotham',
    author_email='nlongbotham@digitalglobe.com',
    packages=find_packages(),
    description='Small, high-level tools that fill gaps in current Python '
                'tool sets.',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    test_suite = 'tinytools.tests'
)
