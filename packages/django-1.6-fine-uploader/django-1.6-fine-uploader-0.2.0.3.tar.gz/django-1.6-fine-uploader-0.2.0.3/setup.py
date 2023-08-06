# !/usr/bin/env python
# encoding:UTF-8

import re
import os
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_version(*file_paths):
    """Retrieves the version from django_fine_uploader/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("django_fine_uploader", "__init__.py")

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-1.6-fine-uploader',
    packages=find_packages(),
    version=version,
    description="""Simple, Chunked and Concurrent uploads with Django + Fine Uploader""",
    long_description=readme + '\n\n' + history,
    author='Team QWL',
    author_email='padova@quag.com',
    url='https://github.com/cic79/django-1.6-fine-uploader',
    download_url='https://github.com/cic79/django-1.6-fine-uploader/archive/%s.tar.gz' % version,
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords=['django', 'fine', 'uploader'],
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        "django<1.7",
        "six",
    ],
)
