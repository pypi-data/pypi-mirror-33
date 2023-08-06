# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join
from setuptools import setup

version_file = join(dirname(abspath(__file__)), 'XsdLibrary', 'version.py')

with open(version_file) as f:
    code = compile(f.read(), version_file, 'exec')
    exec code

setup(
    name='robotframework-xsd',
    version=VERSION,
    description='XSD validator for robotframework',
    author='mangobowl',
    author_email='mangobowl@163.com',
    license='BSD License',
    keywords='robotframework testing test automation xsd schema',
    packages=['XsdLibrary'],
    install_requires=[
        'robotframework<3.0',
        'xmlschema<1.0',
        'validators'
    ],
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing'
    ],
)
