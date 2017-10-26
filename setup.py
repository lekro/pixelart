"""Setup module for pixelart helper
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Read README
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='pixelart',
        version='0.1.1',
        description='Match images to minecraft textures',
        long_description=long_description,
        url='https://github.com/lekro/pixelart',
        author='lekro',
        author_email='kapuraya@gmail.com',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: End Users/Desktop',
            'Topic :: Games/Entertainment',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
        ],
        keywords=['pixel', 'art', 'pixelart', 'minecraft'],
        packages=find_packages(exclude=['contrib', 'docs', 'tests']),
        install_requires=['numpy', 'Pillow'],
        extras_require={
            'faster nearest neighbors matching': ['scipy']
        },
        python_requires='>=3.2',
        entry_points={
            'console_scripts': [
                'pixelart=pixelart:main',
                'pixelart-cli=pixelart:main_cli',
                'pixelart-gui=pixelart:main_gui'
            ],
        }
)
