#!/usr/bin/env python3

from os.path import abspath, dirname, join
from setuptools import setup


here = abspath(dirname(__file__))
with open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    author='heiko huebscher',
    author_email='heiko.huebscher@gmail.com',
    name='csboilerplate',
    description='console script boilerplate',
    keywords='cli console commandline',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=('csboilerplate',),
    url='https://github.com/hbschr/csboilerplate',
    install_requires=[],
    extras_require={
        'dev': [
            'flake8>=3.5.0',
            'pytest>=3.6.0',
            'pytest-cov>=2.5.1',
            'coveralls>=1.3.0',
            'tox>=3.0.0',
        ],
        'doc': [
            'sphinx>=1.7.5',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
