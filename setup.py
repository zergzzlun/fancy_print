# Zhaolun Zou 04/16/2025
from setuptools import setup, find_packages

setup(
    name='fancy_print',
    version='0.1',
    packages=find_packages(),
    author='Zhaolun Zou',
    description=('A tiny utility to print strings character by character '
                 'like animation.'),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'fancy_print=fancy_print.fancy_print:main',
        ],
    },
)
