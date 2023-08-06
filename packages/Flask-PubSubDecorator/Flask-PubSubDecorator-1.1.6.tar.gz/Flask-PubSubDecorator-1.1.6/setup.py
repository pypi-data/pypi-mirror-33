import os
from setuptools import setup, find_packages

__version__ = '1.1.6'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Flask-PubSubDecorator',
    version=__version__,
    description='Decorates publisher functions and subscriber routes creating topics/subscriptions if necessary',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/MobiusWorksLLC/Flask-PubSubDecorator.git',
    author='Tyson Holub',
    author_email='tholub@mobiusworks.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'clint',
        'click',
        'requests',
        'google-cloud-pubsub',
        'gcredstash==1.0.1',
        'Flask'
    ]
)
