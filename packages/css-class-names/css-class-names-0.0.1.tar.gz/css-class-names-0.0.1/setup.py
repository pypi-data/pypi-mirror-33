# coding: utf-8
from setuptools import setup

with open("README.md", "r") as fd:
    README = fd.read()

setup(
    name='css-class-names',
    description='A python script for css class names conditional generation',
    version='0.0.1',
    author='Artur Sousa',
    author_email='arturfelipe.sousa@gmail.com',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/arturfsousa/css-class-names',
    license='MIT',
    py_modules=['css_class_names'],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
