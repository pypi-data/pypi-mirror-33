#from distutils.core import setup
from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='geopicker',
    version='0.1',
    packages=['geopicker',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    install_requires=['pandas', 'geopandas', 'shapely',],
)