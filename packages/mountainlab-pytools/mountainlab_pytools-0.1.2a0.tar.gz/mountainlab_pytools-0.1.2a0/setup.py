"""
Setup Module to setup mountainlab_pytools package
"""
import setuptools

setuptools.setup(
    name='mountainlab_pytools',
    version='0.1.2a',
    description='Tools for integrating MountainLab with python',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ]
)
