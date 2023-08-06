# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

with open("README.rst", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="deeru-qiniu",
    version="1.0.0",
    description="deeru七牛插件",
    long_description=long_description,
    license="GUN V3.0",

    url="https://github.com/gojuukaze/deeru-qiniu",
    author="gojuukaze",
    author_email="i@ikaze.uu.me",
    python_requires='>=3.5',


    packages=find_packages(include=['deeru_qiniu*', ]),


    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',


    ],



)
