'''
Copyright 2018 Scott Prahl

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the 'Software'),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
'''

from setuptools import setup

setup(
    name='iadpython',
    packages=['iadpython'],
    version='0.2.5',
    description='Forward and inverse radiative transport using adding-doubling',
    url='https://github.com/scottprahl/iadpython.git',
    author='Scott Prahl',
    author_email='scott.prahl@oit.edu',
    license='MIT',
    classifiers=[
		'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['absorption', 'scattering', 'reflection',
              'transmission', 'optical properties'],
    zip_safe=False,
    install_requires=['numpy'],
    test_suite='iadpython/test_iadpython.py',
    long_description='''
    A basic python interface to the inverse adding-doubling package written
    in C by Scott Prahl.  This allows users to extract the intrinisic optical 
    properties of materials from measurements of total reflected and total 
    transmitted light.
    
    The original adding-doubling was developed by van de Hulst to model light
    propagation through layered media.  It was extended to handle Fresnel 
    reflection at boundaries as well as interactions with integrating spheres. 
    Finally, the code was further extended to handle lost light by including 
    Monte Carlo techniques.''',
)
