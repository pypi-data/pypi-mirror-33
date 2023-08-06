from setuptools import setup, find_packages
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='messagemedia_signingkeys_sdk',
    version='1.1.0',
    description='The MessageMedia Signature Key API provides a number of endpoints  for managing key used to sign each unique request to ensure security  and the requests can\'t (easily) be spoofed. This is similar to using  HMAC in your outbound messaging (rather than HTTP Basic).',
    long_description=long_description,
    author='MessageMedia Developers',
    author_email='developers@messagemedia.com',
    url='https://developers.messagemedia.com',
    packages=find_packages(),
    install_requires=[
        'requests>=2.9.1, <3.0',
        'jsonpickle>=0.7.1, <1.0',
        'cachecontrol>=0.11.7, <1.0',
        'python-dateutil>=2.5.3, <3.0'
    ],
    tests_require=[
        'nose>=1.3.7'
    ],
    test_suite = 'nose.collector'
)
