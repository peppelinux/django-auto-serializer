import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(name='django-auto-serializer',
    version='0.4.2',
    description="Django app that automates objects tree serialization recursively",
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 5 - Production/Stable',
              'License :: OSI Approved :: BSD License',
              'Programming Language :: Python :: 3 :: Only'],
    url='https://github.com/peppelinux/django-auto-serializer',
    author='Giuseppe De Marco',
    author_email='giuseppe.demarco@unical.it',
    license='BSD',
    packages=['django_auto_serializer'],
    install_requires=[
    'django>=2.0,<4.0',
    ],
)
