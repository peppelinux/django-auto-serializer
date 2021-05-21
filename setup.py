from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='django-auto-serializer',
      version='0.3',
      description="Django app that automates objects tree serialization recursively, wihtout any declaration",
      long_description=readme(),
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
