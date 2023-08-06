import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ping-me',
    version='0.0.1a',
    description='A Django app to create availability statistics of web servers',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/aloha68/django-ping-me',
    author='Aloha',
    author_email='dev@aloha.im',
    license='WTFPL',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django >= 2.0.6',
        'aloha-utils >= 0.0.2',
        'django-cron >= 0.5.1',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications',
    ],
)
