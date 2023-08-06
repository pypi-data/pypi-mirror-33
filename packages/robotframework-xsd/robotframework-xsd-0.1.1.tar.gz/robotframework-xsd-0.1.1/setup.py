# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='robotframework-xsd',
    version='0.1.1',
    description=(
        'xsd for robotframework'
    ),
    author='mangobowl',
    author_email='mangobowl@163.com',
    license='BSD License',
    packages=['XsdLibrary'],
    install_requires=[
        'robotframework<3.0',
        'xmlschema<1.0',
        'validators'
    ],
    platforms=["all"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
)