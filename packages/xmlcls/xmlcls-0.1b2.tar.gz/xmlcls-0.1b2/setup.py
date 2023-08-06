# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='xmlcls',
    version='0.1.b2',
    description='Classes for work with XML elements as objects',
    author='chsergey',
    author_email='chsergey@chsergey.ru',
    license='MIT',
    url='https://github.com/chsergey/xmlcls',
    keywords='xml lxml parsing defusedxml',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup :: XML',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: MIT License',
    ],

    packages=['xmlcls'],

    install_requires=['defusedxml', 'lxml~=4.2.1'],
    python_requires='~=3.3',

    project_urls={
        'Source': 'https://github.com/chsergey/xmlcls',
    },
)
