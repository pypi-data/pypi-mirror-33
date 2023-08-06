# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='fizzbuzz-vaibhav',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],  # dependencies here
    entry_points={
        'console_scripts': [
            'fizzbuzz=fizzbuzz.__main__:main'
        ]
    }
)
