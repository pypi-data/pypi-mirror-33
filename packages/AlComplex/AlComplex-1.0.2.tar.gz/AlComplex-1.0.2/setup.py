import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name = 'AlComplex',
    version = '1.0.2',
    packages = setuptools.find_packages(),

    author = 'Jean Franco Gómez',
    author_email = 'JeanFGomezR@gmail.com',

    description= 'An extended Complex number library',
    
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/Jexan/AlComplex',
)
