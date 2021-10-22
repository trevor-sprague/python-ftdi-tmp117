"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='python-ftdi-tmp117',
    version='0.0.1',
    description='TMP117 library interfacing via FTDI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/trevor-sprague/python-ftdi-tmp117',
    author='Trevor Sprague',
    install_requires=[
        "pyftdi",
    ],
    classifiers=[
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='tmp117, temperature, temp, tmp, ftdi',

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    py_modules=["tmp117-ftdi"],
)