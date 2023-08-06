<h1 align='center'> Django-Gtts </h1>
<p align='center'>
<a href='https://travis-ci.com/mrf345/static_parameters'><img src='https://travis-ci.com/mrf345/static_parameters.svg?branch=master' /></a><a href='https://coveralls.io/github/mrf345/static_parameters?branch=master'><img src='https://coveralls.io/repos/github/mrf345/static_parameters/badge.svg?branch=master' alt='Coverage Status' /></a>
</p>
<h3 align='center'>
    Simple decorators to raise a TypeError, if parameters type not satisfied.
</h3>

## Install:

#### - With pip
> - `pip install static_parameters` <br />

#### - From the source:
> - `git clone https://github.com/mrf345/static_parameters.git`<br />
> - `cd para_meters` <br />
> - `python setup.py install`

## Setup:
```python
from static_parameters import function_parameters

@function_parameters
def example(a, b):
    '''Some example to demo ((a: str)) ((b: str))'''
    return a + b
```
> To decorate all class methods
```python
from static_parameters import (
    function_parameters,
    class_parameters
)

@class_parameters(function_parameters)
class Example:
    def exm1(a, b):
        ''' ((a: bool)), ((b: int))'''
    
    def exm2(a):
        ''' ((a: str)), ...'''
```
> to run test `python test.py`

#### Known issues:
- doesn't work on an interactive shell