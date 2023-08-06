from distutils.core import setup

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pydarg',
    version='0.1',
    description='Pure Python decorator for more complex dictionary handling',
    author='Jeremie Bigras-Dunberry',
    author_email='Bigjerbd@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url='https://github.com/BigJerBD/pydarg',
    license='MIT License',
    platforms=['POSIX', 'Windows', 'Unix', 'MacOS'],
    keywords=['python', 'dictionary', 'decorator', 'configuration', 'utils'],
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "Topic :: Utilities"
    ),
)
