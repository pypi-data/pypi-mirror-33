#from distutils.core import setup
from setuptools import setup, find_packages

install_requires = ['tinytools']

# import __version__
exec(open('dgsamples/_version.py').read())

setup(
    name='dgsamples',
    version=__version__,
    author='Nathan Longbotham',
    author_email='nlongbotham@digitalglobe.com',
    packages=find_packages(),
    description='Sample image chips and vectors that can be used for '\
                'unit testing',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    include_package_data=True
)
