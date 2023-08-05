import os
import sys
from setuptools import setup, find_packages

with open('LONG_DESCRIPTION.rst') as f:
    long_description = f.read()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'templarbit'))

from version import VERSION

setup(
    name='templarbit',
    packages=find_packages(),
    include_package_data=True,
    version=VERSION,
    description='',
    long_description=long_description,
    author='Templarbit Inc.',
    author_email='hello@templarbit.com',
    license='GPLv3',
    url='https://github.com/templarbit/templarbit-python',
    keywords=['templarbit'],
    install_requires=[],
    tests_require=['webtest', 'mock', 'freezegun'],
    test_suite='test.all',
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)
