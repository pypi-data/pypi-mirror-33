from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
setup(
    name='microservices_messaging_layer',
    version='1.0.7',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['avro-python3', 'kafka', 'requests', 'confluent-kafka'],
    url='',
    license='',
    python_requires='~=3.6',
    author='Antonio Di Mariano',
    author_email='antonio.dimariano@gmail.com',
    description='Messaging Communication Layer for Microservices Architecture'
)
