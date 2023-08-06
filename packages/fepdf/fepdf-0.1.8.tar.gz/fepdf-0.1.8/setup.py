# -*- coding: utf-8 -*-
"""A setuptools based setup module"""

from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fepdf',
    version='0.1.8',
    description='Generacion de PDF de Facturas Electrónicas de Argentina',
    long_description=long_description,
    url='https://bitbucket.org/injaon/fepdf/overview',
    author='Gabriel M. Lopez',
    author_email='gabriel.marcos.lopez@gmail.com',
    license='GNU GPL3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='AFIP PDF Factura Argentina',
    py_modules=["fepdf"],
    install_requires=['fpdf'],
    extras_require={
        'dev': ['pep8', 'isort', 'ipython', 'wheel', 'twine'],
        'test': ['coverage'],
    },
)
