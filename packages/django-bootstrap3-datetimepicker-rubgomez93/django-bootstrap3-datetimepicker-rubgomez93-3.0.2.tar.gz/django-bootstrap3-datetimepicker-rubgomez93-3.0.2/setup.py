import sys
from setuptools import setup

long_description = ''
if 'upload' in sys.argv or 'register' in sys.argv:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')

setup(
    name='django-bootstrap3-datetimepicker-rubgomez93',
    packages=['bootstrap3_datetime'],
    maintainer="Ruben Gomez",
    maintainer_email="rubgomez93@gmail.com",
    include_package_data=True,
    version='3.0.2',
    description='Bootstrap3 compatible datetimepicker for Django projects.',
    long_description=long_description,
    author='Nakahara Kunihiko, Samuel Colvin',
    author_email='nakahara.kunihiko@gmail.com, s@muelcolvin.com',
    url='https://github.com/rubgombar1/django-bootstrap3-datetimepicker',
    license='Apache License 2.0',
    classifiers=[
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)
