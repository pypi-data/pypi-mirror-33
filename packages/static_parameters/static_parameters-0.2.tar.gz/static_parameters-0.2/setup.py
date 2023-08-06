"""
static_parameters
-------------
Simple decorators to raise a TypeError, if parameters
and it's static type added to the description __doc__
as such (parameter_name: str) not satisfied.

Example:
from static_parameters import (
    function_parameters,
    class_parameters
)

@function_parameters
def example(a, b):
    '''Some example to demo ((a: str)) ((b: str))'''
    return a + b

# For all methods in a class

@class_parameters(function_parameters)
class Example:
    def exm1(a, b):
        ''' ((a: bool)), ((b: int))
    
    def exm2():
        ...
"""
from setuptools import setup


setup(
    name='static_parameters',
    version='0.2',
    url='https://github.com/mrf345/static_parameters/',
    download_url='https://github.com/mrf345/static_parameters/archive/0.2.tar.gz',
    license='MIT',
    author='Mohamed Feddad',
    author_email='mrf345@gmail.com',
    description='Simple decorators to raise a TypeError, if paramates type not satisfied',
    long_description=__doc__,
    packages=['static_parameters'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    keywords=['static', 'typing', 'parameters', 'decorator'],
    classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
