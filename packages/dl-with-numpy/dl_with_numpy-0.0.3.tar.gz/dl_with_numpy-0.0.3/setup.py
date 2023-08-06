from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='dl_with_numpy',
    version='0.0.3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/jonathan-smith-1/dl_with_numpy',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='MIT License',
    author='Jonathan Smith',
    author_email='jhwsmith86@googlemail.com',
    description='Simple deep learning with numpy',
    install_requires=['numpy'],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
