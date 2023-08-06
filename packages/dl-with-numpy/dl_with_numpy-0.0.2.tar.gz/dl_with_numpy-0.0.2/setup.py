from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='dl_with_numpy',
    version='0.0.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/jonathan-smith-1/dl_with_numpy',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='MIT License',
    author='Jonathan Smith',
    author_email='jhwsmith86@googlemail.com',
    description='Simple deep learning with numpy',
    install_requires=['numpy']
)
