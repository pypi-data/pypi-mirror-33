# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from django_privacy_mgmt import __version__


setup(
    name='django-privacy-mgmt',
    version=__version__,
    description=open('README.md').read(),
    author='what.digital',
    author_email='mario@what.digital',
    packages=find_packages(),
    platforms=['OS Independent'],
    install_requires=[
        'django-parler>=1.8.1',
        'Django>=1.8',
    ],
    download_url='https://gitlab.com/what-digital/django-privacy-mgmt/-/archive/{}/django-privacy-mgmt-{}.tar.gz'.format(
        __version__,
        __version__
    ),
    url='https://gitlab.com/what-digital/django-privacy-mgmt/tree/master',
    include_package_data=True,
    zip_safe=False,
)
