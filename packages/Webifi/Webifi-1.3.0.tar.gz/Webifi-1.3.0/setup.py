from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Webifi',
    version='1.3.0',
    description='Webifi Python Library',
    long_description=long_description,
    url='https://www.webifi.me/python-library-documentation/',
    author='Hubert Jetschko',
    author_email='hubert@webifi.me',
    license='Other/Proprietary License',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='IoT, Internet of Things communication platform',
    install_requires=['websocket-client'],
    packages=['Webifi_p27', 'Webifi_p3'],
)