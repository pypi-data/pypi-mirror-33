from setuptools import setup, find_packages

setup(
    name='woning-wattle',
    version='0.4.0',
    description='Library for converting yaml structures to Python objects, '
                'based on a predefined object hierarchy schema.',
    packages=find_packages(),
    install_requires=[
        'pyyaml'
    ],
    long_description=open('README.md').read(),
    url='https://gitlab.com/woning-group/libs/wattle'
)
