from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='linklabs-conductor',
    version='1.5.4',
    description='Linklabs Conductor API Wrapper',
    long_description=long_description,
    url='https://www.link-labs.com',
    author='Linklabs, LLC',
    author_email='support@link-labs.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='linklabs symphony conductor api',
    packages=find_packages(),
    install_requires=['requests', 'python-dateutil', 'ws4py'],
)
