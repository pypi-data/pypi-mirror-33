from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

with open('README.md') as r:
    readme = r.read()

# with open('AUTHORS.txt') as a:
#     # reSt-ify the authors list
#     authors = ''
#     for author in a.read().split('\n'):
#         authors += '| '+author+'\n'

with open('LICENSE.txt') as l:
    license = l.read()

setup(
    name='configuration_layer',
    version='1.0.8',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    python_requires='~=3.6',
    url='',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    author='Antonio Di Mariano',
    author_email='antonio.dimariano@gmail.com',
    description='Initial configuration layer for microservices',
    long_description=readme + '\n\n' + '\nLicense\n-------\n' + license,
    install_requires=['avro-python3', 'confluent-kafka', 'kafka',
                      'requests',
                      'microservices_messaging_layer',
                      'fastavro']

)
