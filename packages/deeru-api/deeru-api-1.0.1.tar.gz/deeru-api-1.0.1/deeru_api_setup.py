# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

with open("README.rst", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="deeru-api",
    version="1.0.1",
    description="DeerU返回json数据接口",
    long_description=long_description,
    license="GPL V3",

    url="https://github.com/gojuukaze/deeru-api",
    author="gojuukaze",
    author_email="i@ikaze.uu.me",
    python_requires='>=3.5',

    packages=find_packages(include=['deeru_api*', ]),


    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',


    ],


)
