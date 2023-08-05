#!/usr/bin/env python

import re


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = ''
with open('django_upyun/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='django_upyun',
    version=version,
    description='Django 又拍云存储插件',
    long_description=readme,
    packages=['django_upyun'],
    install_requires=['django>=2.0',
                      'upyun>=2.5.1'],
    include_package_data=True,
    url='https://gitee.com/enlangs/django-upyun-storage',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
)
