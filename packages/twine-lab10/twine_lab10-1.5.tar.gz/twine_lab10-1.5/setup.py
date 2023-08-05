# setup.py

import setuptools

cvalidator = setuptools.Extension('cvalidator', sources=['cvalidator.c'])

setuptools.setup(
    name='twine_lab10',
    version='1.5',
    author='Mikolaj Mazurek',
    author_email='mikolajmazurek@gmail.com',
    url='https://github.com/mikolaj965/DPP_Lab10/',
    packages=['lab10'],
    license='MIT',
    description='An example python package',
    ext_modules=[cvalidator],
    long_description=open('README.txt').read(),
)
