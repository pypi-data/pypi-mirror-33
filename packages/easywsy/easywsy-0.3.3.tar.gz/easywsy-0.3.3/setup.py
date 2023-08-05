# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='easywsy',
    version='0.3.3',
    description='Simple Web Service development API based on suds',
    url='https://gitlab.e-mips.com.ar/infra/easywsy',
    author='Martín Nicolás Cuesta',
    author_email='cuesta.martin.n@hotmail.com',
    packages=['easywsy', 'easywsy.api', 'easywsy.ws',
              'easywsy.error', 'easywsy.check'],
    license='AGPL3+',
    install_requires=[
        'suds',
    ],
    zip_safe=False,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
