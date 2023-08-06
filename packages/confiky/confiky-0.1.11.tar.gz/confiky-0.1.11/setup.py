from setuptools import setup, find_packages

setup(
    name='confiky',
    version='0.1.11',
    description='Read one or more .ini config file and return sections and params as object attributes',
    url='https://github.com/acarmisc/confiky',
    author='Andrea Carmisciano',
    author_email='andrea.carmisciano@gmail.com',
    install_requires=['ConfigParser'],
    packages=['confiky']
)

