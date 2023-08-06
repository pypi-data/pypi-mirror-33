from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='drf-request-client',
    version='1.1.0',
    description='Client wrapper for a DRF',

    # long_description=long_description,
    # long_description_content_type='text/markdown',
    url='https://aerobotics.co.za',
    author='Aerobotics',
    author_email='adam@aerobotics.io',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='api aeroview aerobotics request django rest',  # Optional

    packages=['drf_request_client'],

    install_requires=['requests>=2.18.4'],  # Optional
    python_requires='>=2.7',
)