import setuptools
from distutils.core import setup

setup(
    name='hypothesis_client',
    version='0.0.1',
    description='A Python client for interacting with Hypothes.is API',
    long_description='A Python client to fetch API token from Hypothes.is and interact with Hypothes.is API\'s',
    author='Varun Bansal',
    author_email='varunb94@gmail.com',
    license='Apache2',
    url='https://github.com/linuxpi/hypothesis_client',
    packages=setuptools.find_packages(),
    install_requires=['mechanicalsoup', 'requests'],
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    )
)