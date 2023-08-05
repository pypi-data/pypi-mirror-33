import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='python-byterestclient',
    version='20180619.1600',
    url='https://github.com/ByteInternet/python-byterestclient',
    author='Byte B.V.',
    author_email='tech@byte.nl',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: Communications',
        'Topic :: Internet',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='REST client requests json API',
    description='A generic REST client',
    install_requires=['requests'],
    test_suite="tests",
    packages=['byterestclient']
)
