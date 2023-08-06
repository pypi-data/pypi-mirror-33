from setuptools import setup, find_packages
import os


# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='phtml',
    version='0.0.1',
    description='Refactor HTML in Python',
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://github.com/yourlabs/phtml',
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.rst'),
    license='MIT',
    keywords='html',
    tests_require=['tox'],
    extras_require=dict(
        dev=[
          'django>2.1',
          'jinja2',
        ],
    ),
    entry_points={
        'console_scripts': [
            'phtml-django = phtml.django.example:manage',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
