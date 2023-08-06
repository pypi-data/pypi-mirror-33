# Setup file

from setuptools import setup

setup(
    name='check-exercises',
    version=1.0,
    description='Checks your Codeup exercises to find any missing files',
    url='https://github.com/xaviersalazar/check-exercises',
    author='Xavier Salazar',
    author_email='salazar.xavier26@gmail.com',
    license='MIT',
    packages=['check-exercises'],
    install_requires=['gitpython'],
    python_requires='~=3.3',
    zip_safe=False)