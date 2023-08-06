from setuptools import setup, find_packages

setup(
    name='woning-wattle',
    version='0.4.1',
    description='Library for converting yaml structures to Python objects, '
                'based on a predefined object hierarchy schema.',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='https://gitlab.com/woning-group/libs/wattle',
    packages=find_packages(),
    install_requires=[
        'pyyaml'
    ],
)
