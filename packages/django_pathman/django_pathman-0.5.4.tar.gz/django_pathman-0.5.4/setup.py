# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='django_pathman',
    version='0.5.4',
    author='Ruslan Gilfanov',
    author_email='rg@informpartner.com',
    packages=find_packages(),
    package_dir={'django_pathman': 'django_pathman'},
    package_data={
        'django_pathman': ['sql/*']
    },
)
