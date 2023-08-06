from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

packages = find_packages()

setup(
    name='termcolor_util',
    version='1.0.0',
    description='termcolor_util',
    long_description=readme,
    author='Bogdan Mustiata',
    author_email='bogdan.mustiata@gmail.com',
    license='BSD',
    install_requires=["termcolor==1.1.0"],
    packages=packages,
    package_data={
        '': ['*.txt', '*.rst']
    })
