from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='object-validation',
    version='0.0.1',
    description='An object schema validation',
    url='https://github.com/darrikonn/object-validation',
    author='Darri Steinn Konn Konradsson',
    author_email='darrikonn@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    intended_audience='Developers',
    keywords='object schema validation',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    package_dir={'object_validation': 'object_validation'},
    project_urls={
        'Source': 'https://github.com/darrikonn/object-validation',
    },
)
