#!/usr/bin/env python3
from setuptools import find_packages, setup


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='rectify',
    version=__import__('rectify').__version__,
    author='Ivana Kellyerova',
    author_email='ivana.kellyerova@rectify.amarion.net',
    description=__import__('rectify').__tagline__,
    url='https://gitlab.com/jenx/rectify/',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords=[
        'image',
        'bars',
        'stripe',
        'avatar',
        'generator',
        'rectangle',
        'colors',
    ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics',
    ],
    install_requires=[
        'docopt',
        'Pillow',
        'sphinx',
        'sphinxcontrib-napoleon',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'rectify = rectify.main:main',
        ],
    },
)
