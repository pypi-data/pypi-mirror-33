#!/usr/bin/env python
"""
mitoo setup file.
"""
from setuptools import setup


# Dynamically retrieve the version information from the mitoo module
mitoo = __import__('mitoo')
VERSION = mitoo.__version__
AUTHOR = mitoo.__author__
AUTHOR_EMAIL = mitoo.__email__
URL = mitoo.__url__
DESCRIPTION = mitoo.__doc__

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

with open('requirements.txt') as requirements:
    REQUIREMENTS = requirements.readlines()

setup(
    name='mitoo',
    version=VERSION,
    url=URL,
    download_url='{}/tarball/{}'.format(URL, VERSION),
    project_urls={
        'Documentation': 'https://mitoo.readthedocs.io',
    },
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=[
        'mitoo',
        'mitoo.input',
        'mitoo.output',
        'mitoo.storage',
        'mitoo.logic',
        'mitoo.ext',
        'mitoo.ext.sqlalchemy_app'
    ],
    package_dir={'mitoo': 'mitoo'},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    python_requires='>=2.7, <4',
    license='BSD',
    zip_safe=True,
    platforms=['any'],
    keywords=['mitoo', 'chatbot', 'chat', 'bot'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=['mock']
)
